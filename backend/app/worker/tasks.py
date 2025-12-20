import os
import shutil
import subprocess
import time
import shlex
import json
from uuid import UUID
from typing import List, Tuple, Dict

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.submission import Submission, SubmissionStatus
from app.models.problem import Problem, TestCase

DATA_DIR = os.getenv("DATA_DIR", "/data")
SUBMISSION_DIR = os.path.join(DATA_DIR, "submissions")

# Slurm Settings
SLURM_HOST = os.getenv("SLURM_HOST", "slurm")
SLURM_USER = os.getenv("SLURM_USER", "admin")
SLURM_PASSWORD = os.getenv("SLURM_PASSWORD", "admin")

def parse_slurm_memory(mem_str: str) -> int:
    if not mem_str:
        return 0
    
    mem_str = mem_str.strip()
    if not mem_str or mem_str == "0":
        return 0

    units = {'K': 1, 'M': 1024, 'G': 1024*1024, 'T': 1024*1024*1024}
    suffix = mem_str[-1].upper()
    
    try:
        if suffix in units:
            value = float(mem_str[:-1])
            return int(value * units[suffix])
        else:
            return int(float(mem_str))
    except:
        return 0

def get_job_stats(job_id: str) -> Tuple[str, int, int]:

    sacct_cmd = [
        "sshpass", "-p", SLURM_PASSWORD,
        "ssh", "-o", "StrictHostKeyChecking=no", f"{SLURM_USER}@{SLURM_HOST}",
        f"sacct -j {job_id} --format=State,ElapsedRaw,MaxRSS -n -p"
    ]

    try:
        for _ in range(3):
            result = subprocess.run(sacct_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stdout.strip():
                break
            time.sleep(1)

        output = result.stdout.strip()
        
        max_time_sec = 0
        max_mem_kb = 0
        final_state = "COMPLETED"

        for line in output.split('\n'):
            parts = line.split('|')
            if len(parts) < 3:
                continue
            
            state = parts[0].split()[0]
            time_raw = parts[1]
            mem_raw = parts[2]

            if "TIMEOUT" in state:
                final_state = "TIMEOUT"
            elif "OUT_OF_MEMORY" in state and final_state != "TIMEOUT":
                final_state = "OUT_OF_MEMORY"
            elif "FAILED" in state and final_state not in ["TIMEOUT", "OUT_OF_MEMORY"]:
                final_state = "FAILED"
            elif "CANCELLED" in state:
                final_state = "CANCELLED"

            try:
                t = int(float(time_raw))
                if t > max_time_sec:
                    max_time_sec = t
            except:
                pass

            m = parse_slurm_memory(mem_raw)
            if m > max_mem_kb:
                max_mem_kb = m

        return final_state, max_time_sec * 1000, max_mem_kb

    except Exception as e:
        print(f"Error parsing sacct: {e}")
        return "ERR", 0, 0


def compile_code(work_dir: str, code: str, compile_cmd_template: str, language: str) -> Tuple[bool, str]:
    if language == "cpp":
        source_filename = "source.cpp"
    elif language == "c":
        source_filename = "source.c"
    else:
        source_filename = "source.txt"

    source_file = os.path.join(work_dir, source_filename)
    exe_file = os.path.join(work_dir, "main")

    try:
        with open(source_file, "w") as f:
            f.write(code)
    except Exception as e:
        return False, f"System Error: Failed to write source code. {str(e)}"
    
    if not compile_cmd_template:
        return True, "No compilation required"

    try:
        cmd_str = compile_cmd_template.format(source=source_file, output=exe_file)
        cmd_args = shlex.split(cmd_str)
    except Exception as e:
        return False, f"Command Format Error: {e}"
        
    try:
        result = subprocess.run(
            cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return False, result.stderr
        
        return True, "Compilation successful"
    
    except subprocess.TimeoutExpired:
        return False, "Compilation timeout"
    
    except Exception as e:
        return False, f"Compiler System Error: {str(e)}"


def run_with_slurm(work_dir: str, input_path: str, problem: Problem, run_cmd_template: str) -> Tuple[str, str, int]:
    slurm_script_path = os.path.join(work_dir, "job.slurm")
    output_file = os.path.join(work_dir, "slurm.out")
    error_file = os.path.join(work_dir, "slurm.err")
    exe_file = os.path.join(work_dir, "main")

    try:
        real_run_cmd = run_cmd_template.format(
            exe=exe_file, 
            input=input_path, 
            core_number=problem.core_number
        )
    except Exception as e:
        return "ERR", f"Run Command Format Error: {e}", 0


    slurm_content = f"""#!/bin/bash
#SBATCH --job-name=judge_{os.path.basename(work_dir)}
#SBATCH --nodes=1
#SBATCH --ntasks={problem.core_number}
#SBATCH --output={output_file}
#SBATCH --error={error_file}
#SBATCH --time=00:01:00
#SBATCH --mem={problem.memory_limit}M

{real_run_cmd}
"""
    try:
        with open(slurm_script_path, "w") as f:
            f.write(slurm_content)
    except Exception as e:
        return "ERR", f"Failed to write slurm script: {e}", 0


    cmd = [
        "sshpass", "-p", SLURM_PASSWORD,
        "ssh", "-o", "StrictHostKeyChecking=no", f"{SLURM_USER}@{SLURM_HOST}",
        "sbatch", "--parsable", "--wait", slurm_script_path
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=(problem.time_limit / 1000) + 15 
        )
        
        job_id = result.stdout.strip()
        
        slurm_state, time_ms, memory_kb = get_job_stats(job_id)

        user_output = ""
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                user_output = f.read().strip()
        
        err_msg = ""
        if os.path.exists(error_file):
            with open(error_file, "r") as f:
                raw_err = f.read().strip()
                if raw_err and "slurm" not in raw_err.lower():
                    err_msg = raw_err

        if "TIMEOUT" in slurm_state:
            return "TLE", "", int(problem.time_limit)
        
        if "OUT_OF_MEMORY" in slurm_state:
            return "MLE", "", time_ms
        
        if "FAILED" in slurm_state or (result.returncode != 0 and result.returncode != 255): 
            return "RE", err_msg if err_msg else "Runtime Error", time_ms
        
        if err_msg:
            return "RE", err_msg, time_ms

        return "OK", user_output, time_ms

    except subprocess.TimeoutExpired:
        job_name = f"judge_{os.path.basename(work_dir)}"
        subprocess.run(["sshpass", "-p", SLURM_PASSWORD, "ssh", f"{SLURM_USER}@{SLURM_HOST}", "scancel", "--name", job_name])
        return "TLE", "", int(problem.time_limit)
        
    except Exception as e:
        return "ERR", str(e), 0


@celery_app.task(name="judge_submission")
def judge_submission(submission_id: str):
    print(f"[Worker] Processing Submission: {submission_id}")
    db = SessionLocal()
    
    work_dir = os.path.join(SUBMISSION_DIR, submission_id)
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
        os.chmod(work_dir, 0o777)

    try:
        sub = db.query(Submission).filter(Submission.id == UUID(submission_id)).first()
        if not sub:
            print("Submission not found")
            return

        problem = sub.problem
        if not problem:
            print("Problem not found")
            sub.status = SubmissionStatus.ERR
            db.commit()
            return

        sub.status = SubmissionStatus.JUDGING
        db.commit()

        compile_cmd_template = problem.compile_command 
        run_cmd_template = problem.run_command

        is_compiled, msg = compile_code(work_dir, sub.code, compile_cmd_template, sub.language)
        if not is_compiled:
            sub.status = SubmissionStatus.CE
            sub.result_details = json.dumps({"msg": msg})
            db.commit()
            return

        exe_path = os.path.join(work_dir, "main")
        if os.path.exists(exe_path):
            os.chmod(exe_path, 0o777)

        test_cases = problem.test_cases
        
        final_status = SubmissionStatus.AC
        total_time = 0
        details = []

        for case in test_cases:
            input_full_path = os.path.join(DATA_DIR, case.input_path)
            output_full_path = os.path.join(DATA_DIR, case.output_path)
            
            if not os.path.exists(input_full_path):
                final_status = SubmissionStatus.ERR
                details.append({"status": "ERR", "msg": "Input file missing"})
                break

            status, output, duration = run_with_slurm(
                work_dir, 
                input_full_path, 
                problem, 
                run_cmd_template
            )
            
            total_time += duration
            case_result = {"status": status, "time": duration}

            if status == "OK":
                expected_output = ""
                if os.path.exists(output_full_path):
                    with open(output_full_path, "r") as f:
                        expected_output = f.read().strip()
                
                if output == expected_output:
                    case_result["status"] = "AC"
                else:
                    case_result["status"] = "WA"
                    case_result["user_out"] = output[:100] + "..." if len(output) > 100 else output
                    case_result["expected"] = expected_output[:100] + "..." if len(expected_output) > 100 else expected_output
                    final_status = SubmissionStatus.WA
            else:
                case_result["status"] = status
                case_result["msg"] = output
                if status == "TLE":
                    final_status = SubmissionStatus.TLE
                elif status == "MLE":
                    try:
                        final_status = SubmissionStatus(status)
                    except:
                        final_status = SubmissionStatus.RE
                elif status == "RE":
                    final_status = SubmissionStatus.RE
                else:
                    final_status = SubmissionStatus.ERR

            details.append(case_result)

            if case_result["status"] != "AC":
                break

        sub.status = final_status
        sub.execute_time = total_time
        sub.result_details = json.dumps(details)
        db.commit()
        print(f"Judge Finished: {final_status}")

    except Exception as e:
        print(f"Worker Exception: {e}")
        db.rollback()
        sub.status = SubmissionStatus.ERR
        sub.result_details = json.dumps({"error": str(e)})
        db.commit()
    finally:
        db.close()