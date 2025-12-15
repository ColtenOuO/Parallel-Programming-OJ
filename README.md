# Parallel-Programming-OJ
多處理機平行程式設計 Online Judge

## Quick Start

### Backend

#### Prerequisites

- Miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

- PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

#### Setup

```bash
cd backend
conda env create -f environment.yml
conda activate poj_backend
```
