#!/bin/bash
echo "arch:     $(uname -m)"
echo "os:       $(. /etc/os-release; echo $PRETTY_NAME)"
echo "glibc:    $(ldd --version | head -1)"
echo "python:   $(python3 --version)"
echo "ram:      $(free -m | awk '/Mem:/ {print $2" MB total, "$7" MB available"}')"
echo "disk:     $(df -h / | awk 'NR==2 {print $4" free"}')"
echo "cores:    $(nproc)"
echo "temp:     $(vcgencmd measure_temp 2>/dev/null)"
echo "throttle: $(vcgencmd get_throttled 2>/dev/null)"
echo "governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)"
echo "route:    $(ip route | grep default || echo none)"
python3 -c "import executorch; print('executorch: import ok')" 2>&1 | tail -1
