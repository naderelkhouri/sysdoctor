#!/usr/bin/env python3
try:
    import psutil
except ImportError:
    print("psutil não instalado. Execute:")
    print("sudo apt install python3-psutil")
    sys.exit(1)
import os, sys, subprocess, datetime, time, psutil, shutil


# ─── CORES ─────────────────────────────────────────
class C:
    R="\033[0m"; B="\033[1m"
    G="\033[92m"; Y="\033[93m"; R2="\033[91m"
    C="\033[96m"; D="\033[90m"

# ─── CORE ──────────────────────────────────────────
def run(cmd, show=True):
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if show and r.stdout:
            print(r.stdout)
        return r.returncode, r.stdout
    except:
        return 1, ""

# ─── DETECÇÃO ──────────────────────────────────────
def detectar_distro():
    try:
        with open("/etc/os-release") as f:
            data = f.read().lower()
            if "mint" in data: return "Linux Mint"
            elif "ubuntu" in data: return "Ubuntu"
            elif "debian" in data: return "Debian"
    except:
        pass
    return "Linux"

def tem_snap(): return shutil.which("snap") is not None
def tem_flatpak(): return shutil.which("flatpak") is not None

# ─── UI ────────────────────────────────────────────
def clear(): os.system("clear")

def line(): print(f"{C.D}{'─'*60}{C.R}")

def box(t):
    print(f"{C.C}╔{'═'*60}╗{C.R}")
    print(f"{C.C}║ {t.ljust(59)}║{C.R}")
    print(f"{C.C}╚{'═'*60}╝{C.R}")

def bar(p):
    w=30
    f=int(w*p/100); e=w-f
    c=C.G if p<60 else C.Y if p<85 else C.R2
    return f"{c}{'█'*f}{'░'*e}{C.R} {p:5.1f}%"

def header():
    now = datetime.datetime.now().strftime("%d/%m %H:%M:%S")
    distro = detectar_distro()
    print(f"{C.B}{C.C}🩺 SysDoctor{C.R} {C.D}{now} | {distro}{C.R}")
    line()

# ─── DISCO ─────────────────────────────────────────
def disks():
    IGN_FS=("tmpfs","squashfs","devtmpfs")
    IGN=("/snap","/run","/proc","/sys")
    return [
        p for p in psutil.disk_partitions(all=False)
        if p.fstype.lower() not in IGN_FS
        and not any(p.mountpoint.startswith(x) for x in IGN)
    ]

# ─── SNAP ──────────────────────────────────────────
def snaps_old():
    if not tem_snap(): return []
    _, out = run(["snap","list","--all"], False)
    lines = out.splitlines()[1:]
    return [(l.split()[0], l.split()[2]) for l in lines if len(l.split())>=6 and l.split()[-1]=="disabled"]

def clean_snaps():
    if not tem_snap(): return
    for name, rev in snaps_old():
        run(["snap","remove", name, "--revision", rev], False)

# ─── FLATPAK ───────────────────────────────────────
def flatpak_updates():
    if not tem_flatpak(): return []
    _, out = run(["flatpak","remote-ls","--updates"], False)
    return out.splitlines()

# ─── APT ───────────────────────────────────────────
def analyze_updates():
    run(["apt-get","update","-qq"], False)

    _, out = run(["apt","list","--upgradable"], False)
    pkgs = [l for l in out.splitlines() if "/" in l]

    _, sec = run(["apt-get","-s","upgrade"], False)
    security = [l for l in sec.splitlines() if "security" in l.lower()]

    _, full = run(["apt-get","-s","full-upgrade"], False)
    phased = "faseamento" in full.lower()

    return len(pkgs), len(security), phased

# ─── REBOOT ────────────────────────────────────────
def reboot_needed():
    return os.path.exists("/var/run/reboot-required")

# ─── SCORE ─────────────────────────────────────────
def score_calc(problems, cpu, mem):
    score = 100
    if cpu>90: score-=15
    if mem>90: score-=15
    for p in problems:
        if p=="security": score-=30
        elif p=="update": score-=10
        elif p=="snap": score-=5
    return max(score,0)

# ─── AUTO FIX ──────────────────────────────────────
def auto_fix():
    clear(); header(); box("AUTO CORREÇÃO")

    run(["apt-get","update"])
    run(["apt-get","full-upgrade","-y"])

    if tem_snap():
        run(["snap","refresh"])
        clean_snaps()

    if tem_flatpak():
        run(["flatpak","update","-y"])

    run(["apt-get","autoremove","-y"])
    run(["apt-get","autoclean","-y"])
    run(["apt-get","clean"])

    print(f"{C.G}✔ Sistema atualizado e limpo{C.R}")
    input()

# ─── RELATÓRIO ─────────────────────────────────────
def report():
    clear(); header(); box("RELATÓRIO")

    problems=[]

    cpu = psutil.cpu_percent(1)
    mem = psutil.virtual_memory().percent

    print(f" CPU  {bar(cpu)}")
    print(f" RAM  {bar(mem)}\n")

    if cpu>90: problems.append("cpu")
    if mem>90: problems.append("mem")

    box("DISCO")
    for d in disks():
        try:
            u = psutil.disk_usage(d.mountpoint).percent
            print(f" {d.mountpoint:<12} {bar(u)}")
            if u>85: problems.append("disk")
        except: pass

    print()

    box("PACOTES")
    if tem_snap():
        snaps = snaps_old()
        print(f" Snap: {len(snaps)} antigos" if snaps else " Snap: OK")
        if snaps: problems.append("snap")
    else:
        print(" Snap: não instalado")

    if tem_flatpak():
        f = flatpak_updates()
        print(f" Flatpak: {len(f)} updates" if f else " Flatpak: OK")
    else:
        print(" Flatpak: não instalado")

    print()

    box("UPDATES")
    total, security, phased = analyze_updates()

    if security:
        print(f"{C.R2}{security} segurança{C.R}")
        problems.append("security")

    if total:
        if phased:
            print(f"{C.Y}{total} faseadas{C.R}")
        else:
            print(f"{C.Y}{total} pendentes{C.R}")
            problems.append("update")
    else:
        print(f"{C.G}OK{C.R}")

    print()

    box("REBOOT")
    if reboot_needed():
        print(f"{C.Y}Necessário{C.R}")
        problems.append("reboot")
    else:
        print(f"{C.G}Não{C.R}")

    print()

    score = score_calc(problems, cpu, mem)

    box("HEALTH SCORE")
    cor = C.G if score>80 else C.Y if score>60 else C.R2
    print(f"{cor}{score}/100{C.R}")

    print()

    box("AÇÃO")
    if "security" in problems:
        print(" • Atualizar imediatamente")
    elif "update" in problems:
        print(" • Rodar auto correção")
    elif "reboot" in problems:
        print(" • Reiniciar sistema")
    else:
        print(" • Sistema OK")

    input("\nEnter...")

# ─── MONITOR ───────────────────────────────────────
def monitor():
    try:
        while True:
            clear(); header()

            cpu = psutil.cpu_percent(1)
            mem = psutil.virtual_memory().percent

            box("STATUS")
            print(f" CPU  {bar(cpu)}")
            print(f" RAM  {bar(mem)}\n")

            box("DISCO")
            for d in disks():
                try:
                    u = psutil.disk_usage(d.mountpoint).percent
                    print(f" {d.mountpoint:<12} {bar(u)}")
                except: pass

            print(f"\n{C.D}Ctrl+C para sair{C.R}")
            time.sleep(2)

    except KeyboardInterrupt:
        pass

# ─── MENU ──────────────────────────────────────────
def menu():
    while True:
        clear(); header()

        print(f"""
{C.C}╔════════════════════════════════╗
║ 1 Relatório completo           ║
║ 2 Auto correção                ║
║ 3 Monitor tempo real           ║
║ 0 Sair                         ║
╚════════════════════════════════╝{C.R}
""")

        op = input(">> ")

        if op=="1": report()
        elif op=="2": auto_fix()
        elif op=="3": monitor()
        elif op=="0": break

# ─── MAIN ──────────────────────────────────────────
if __name__=="__main__":
    if os.geteuid()!=0:
        print("sudo required"); sys.exit(1)
    menu()