import runpy
import sys, time
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Uso: python run_timed.py caminho/para/script.py [args...]")
        sys.exit(1)

    script = sys.argv[1]
    args = sys.argv[2:]

    # Simular argv do script alvo
    sys.argv = [script, *args]

    t0 = time.perf_counter()
    try:
        runpy.run_path(script, run_name="__main__")
    finally:
        dt = time.perf_counter() - t0
        print(f"[TIMER] {Path(script).name} levou {dt:.3f}s")

if __name__ == "__main__":
    main()
