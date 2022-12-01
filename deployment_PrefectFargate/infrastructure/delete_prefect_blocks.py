import subprocess
import sys
   

def delete_blocks(blocks):   
    for block in blocks:
        subprocess.run(f"prefect block delete {block}", shell=True)    


if __name__ == '__main__':
    if len(sys.argv) > 1:
        blocks =  list(sys.argv[1:])
        delete_blocks(blocks)
    else:
        raise SystemExit("No blocks passed.")
