"""Measure a fresh Linux process through indexing, search, and benchmarking.

Run with: docker compose run --rm --no-deps search .venv/bin/python -m src.memory_probe
Stop the existing service first on small machines to avoid a second model.
Linux resource/proc values describe this process, not total container memory.
"""
import json
from pathlib import Path
from time import perf_counter


def measure():
    # resource is available in the Linux deployment image, not native Windows.
    import resource
    from .workbench import Workbench

    def snapshot():
        status=Path("/proc/self/status").read_text()
        rss_kib=int(status.split("VmRSS:",1)[1].split()[0])
        peak_kib=max(int(status.split("VmHWM:",1)[1].split()[0]),
                     resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        return {"rss_mib":round(rss_kib/1024,1),
                "peak_mib":round(peak_kib/1024,1)}

    started=perf_counter()
    workbench=Workbench()
    indexed=snapshot()
    build_seconds=perf_counter()-started
    for case in workbench.cases:
        workbench.compare(case.query,5,"structural")
    benchmark=workbench.benchmark()
    return {"scope":"Fresh Linux Python process; not total container usage",
            "build_seconds":round(build_seconds,2),"after_indexing":indexed,
            "after_search_and_benchmark":snapshot(),
            "quality_at_5":[{key:row[key] for key in ("strategy","hit_rate","recall","mrr")}
                            for row in benchmark["rows"] if row["k"]==5]}


if __name__=="__main__":
    print(json.dumps(measure(),indent=2))
