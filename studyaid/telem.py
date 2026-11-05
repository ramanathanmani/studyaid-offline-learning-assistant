import os
import sys
import platform
import subprocess
import resource
import psutil

def get_net_state():
    if platform.system() == "Linux":
        try:
            link_out = subprocess.check_output(["ip", "-br", "link"], text=True, stderr=subprocess.DEVNULL)
        except Exception:
            link_out = ""
        try:
            route_out = subprocess.check_output(["ip", "route"], text=True, stderr=subprocess.DEVNULL)
        except Exception:
            route_out = ""
        
        ifaces = []
        for line in link_out.strip().splitlines():
            parts = line.split()
            if len(parts) >= 2:
                ifaces.append({"name": parts[0], "state": parts[1]})
                
        has_def = "default" in route_out
        is_off = (not has_def) and all(it["state"] == "DOWN" for it in ifaces if it["name"] != "lo")
        return {
            "method": "linux_ip_cmd",
            "ifaces": ifaces,
            "has_def_route": has_def,
            "is_offline": is_off
        }
    else:
        stats = psutil.net_if_stats()
        ifaces = [{"name": k, "state": "UP" if v.isup else "DOWN"} for k, v in stats.items()]
        has_def = any(v.isup for k, v in stats.items() if k != "lo")
        is_off = (not has_def) and all(it["state"] == "DOWN" for it in ifaces if it["name"] != "lo")
        return {
            "method": "psutil_fallback",
            "ifaces": ifaces,
            "has_def_route": has_def,
            "is_offline": is_off
        }

def get_host_info():
    is_pi = False
    if os.path.exists("/proc/device-tree/model"):
        try:
            with open("/proc/device-tree/model", "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if "Raspberry Pi" in content:
                    is_pi = True
        except Exception:
            pass
    host_lbl = "HOST: Raspberry Pi" if is_pi else "HOST: laptop (not Raspberry Pi)"
    
    cpu_model = platform.processor() or "Unknown CPU"
    if os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line:
                        cpu_model = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass
            
    tot_ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    
    return {
        "host_label": host_lbl,
        "is_pi": is_pi,
        "cpu_model": cpu_model,
        "cores": os.cpu_count() or 1,
        "ram_gb": tot_ram_gb,
        "os": f"{platform.system()} {platform.release()}"
    }

def get_peak_rss_mib():
    try:
        ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if platform.system() == "Darwin":
            return round(ru / (1024 * 1024), 2)
        return round(ru / 1024, 2)
    except Exception:
        proc = psutil.Process()
        return round(proc.memory_info().rss / (1024 * 1024), 2)

def get_peak_rss_mb():
    return get_peak_rss_mib()

def collect_telem(m_name, pte_path, tok_cnt, inf_time, is_mock):
    net = get_net_state()
    host = get_host_info()
    peak_rss = get_peak_rss_mib()
    
    pte_sz_b = None
    pte_sz_mib = None
    if pte_path and os.path.exists(pte_path):
        pte_sz_b = os.path.getsize(pte_path)
        pte_sz_mib = round(pte_sz_b / (1024 * 1024), 2)
        
    tps = round(tok_cnt / inf_time, 2) if inf_time > 0 and not is_mock else 0.0
    
    return {
        "net": net,
        "host": host,
        "model_name": m_name,
        "pte_path": pte_path,
        "pte_size_bytes": pte_sz_b,
        "pte_size_mib": pte_sz_mib,
        "pte_size_mb": pte_sz_mib,
        "peak_rss_mib": peak_rss,
        "peak_rss_mb": peak_rss,
        "inf_time_sec": round(inf_time, 3),
        "tok_cnt": tok_cnt,
        "tok_per_sec": tps,
        "is_mock": is_mock
    }
