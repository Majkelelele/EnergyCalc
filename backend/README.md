# Backend installation as package
https://stackoverflow.com/questions/77507389/python-project-directory-structure-modulenotfounderror

## Creating venv
1) python3 -m venv .venv (thist step needed only when doing this for the first time)
2) source .venv/bin/activate

! **Before proceeding you should install packages from requirements.txt to venv** !

## Installing our project as package
To invoke below command we need to be in a directory with **pyproject.toml**
- cd backend
- pip install -e .

!!! Don't know why pip install -e . creates egg folder, after removing it 
project still works fine !!!

# Battery charging formulas
Formula we use in Battery.charging_time is from below site in method 4
- https://www.jackery.com/blogs/knowledge/how-to-calculate-battery-charging-time