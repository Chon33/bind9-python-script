########################################################################################################################
# $$$$$$$\  $$\   $$\  $$$$$$\                                            $$$$$$$\  $$\                 $$\  $$$$$$\   #
# $$  __$$\ $$$\  $$ |$$  __$$\                                           $$  __$$\ \__|                $$ |$$  __$$\  #
# $$ |  $$ |$$$$\ $$ |$$ /  \__|       $$$$$$$\  $$$$$$\  $$$$$$$\        $$ |  $$ |$$\ $$$$$$$\   $$$$$$$ |$$ /  $$ | #
# $$ |  $$ |$$ $$\$$ |\$$$$$$\        $$  _____|$$  __$$\ $$  __$$\       $$$$$$$\ |$$ |$$  __$$\ $$  __$$ |\$$$$$$$ | #
# $$ |  $$ |$$ \$$$$ | \____$$\       $$ /      $$ /  $$ |$$ |  $$ |      $$  __$$\ $$ |$$ |  $$ |$$ /  $$ | \____$$ | #
# $$ |  $$ |$$ |\$$$ |$$\   $$ |      $$ |      $$ |  $$ |$$ |  $$ |      $$ |  $$ |$$ |$$ |  $$ |$$ |  $$ |$$\   $$ | #
# $$$$$$$  |$$ | \$$ |\$$$$$$  |      \$$$$$$$\ \$$$$$$  |$$ |  $$ |      $$$$$$$  |$$ |$$ |  $$ |\$$$$$$$ |\$$$$$$  | #
# \_______/ \__|  \__| \______/        \_______| \______/ \__|  \__|      \_______/ \__|\__|  \__| \_______| \______/  #
#                                                                                                                      #
#                            Hecho por su dani su totito wapo, regalale un bocadillito <3                              #
#                                                                                                                      #
########################################################################################################################

# constantes globales
import shutil
bind_path = "/etc/bind"


# importar o instalar rich
import pip
import sys
import importlib.util

def importrich(spec) -> None:
    module = importlib.util.module_from_spec(spec)
    sys.modules["rich"] = module
    spec.loader.exec_module(module)
    print("[OK] Rich esta importado\n")

if (spec := importlib.util.find_spec("rich")) is not None:
    importrich(spec)
else:
    print("[ERROR] Rich no esta instalado...\n[INFO] Instalando Rich")
    pip.main(['install', 'rich'])
    if (spec := importlib.util.find_spec("rich")) is not None:
        importrich(spec)


# importar modulos de rich
from rich.prompt import Prompt
from rich import print


def addregla(dom: str, PTR: bool = False) -> str:
    if not PTR:
        t = Prompt.ask("Quieres hacer un [bold blue]dominio[/bold blue] o un [bold blue]cname[/bold blue]?",
        choices=["dominio", "cname"]).lower()

        if t == "cname":
            nuevo_nombre = Prompt.ask("Que nombre le quieres poner?").lower()
            dominio = Prompt.ask("A que dominio?").lower()
            return f"{nuevo_nombre}\tIN\tCNAME\t{dominio}.{dom}."

        else:
            nuevo_nombre = Prompt.ask("Que nombre le quieres poner?").lower()
            ip = Prompt.ask("Que IP le quieres dar?")
            return f"{nuevo_nombre}\tIN\tA\t{ip}"
    else:
        nombre = Prompt.ask(f"Nombre del registro A para convertir a inversa? (sin el nombre de la zona [blue]{dom}[/blue])")
        ip = Prompt.ask("IP del PTR? (Solo el ultimo dígito X.X.X.[blue]X[/blue])")
        return f"{ip}\tIN\tPTR\t{nombre}.{dom}."


def append(file: str, lines: 'list[str]') -> None:
    with open(f"{bind_path}/{file}", "a+") as f:
        f.write('\n'.join(lines) + '\n')
        f.seek(0)
        print(f"\n[FILE][bold cyan] {file}[/bold cyan]: \n")
        for l in f.readlines():
            if not l.startswith("//") and not l.startswith(";") and l.strip():
                print(l, end='')
        print("\n")
        f.close()


def printinfo(IP: str, DOMINIO: str) -> None:
    print(f"[bold][[cyan]INFO[/cyan]] recuarda cambiar la IP del PC y de asegurarte de cual es la puente y cual es la interna[/bold]")
    print(f"[bold][[cyan]INFO[/cyan]] edita la configuracion del cliente, añade la ip del dns ([blue]{IP}[/blue]) y el dominio de busqueda ([blue]{DOMINIO}[/blue])[/bold]")
    print(f"[bold][[cyan]INFO[/cyan]] los archivos se encuentran en [blue]{bind_path}[/blue], puedes editarlos manualmente con [blue]nano[/blue] [/bold]")
    print(f"[bold][[cyan]INFO[/cyan]] puedes hacer pruebas con el comando [blue]host[/blue] o [blue]ping[/blue] seguido del nombre de un host o ip que hayas añadido[/bold]")


# Directa
def directa() -> None:
    print("\n[[bold red blink]![/bold red blink]] Estas añadiendo una regla directa")
    DOMINIO = Prompt.ask(" - Nombre de la zona").lower()
    IP = Prompt.ask(" - IP del servidor ( SIN EL /24 )")

    lines = [
       f"zone \"{DOMINIO}\" {'{'}",
        "    type master;",
       f"    file \"{bind_path}/db.{DOMINIO}\";",
        "}"
    ]

    append("named.conf.local", lines)

    # crear db.dominio
    shutil.copy2(f"{bind_path}/db.local", f"{bind_path}/db.{DOMINIO}")

    # editar db.dominio
    with open(f"{bind_path}/db.{DOMINIO}", "r+") as f:
        filedata = f.read()
        filedata = filedata.replace("localhost", DOMINIO)
        filedata = filedata.replace("127.0.0.1", IP)
        f.seek(0)
        f.write(filedata)
        f.close()

    # añadir reglas
    reglas = []
    print("Las reglas son asi una vez formateadas:")
    print("[bold yellow]name[/bold yellow]    IN    A        [bold yellow]IP[/bold yellow]")
    print("[bold yellow]name[/bold yellow]    IN    CNAME    [bold yellow]nombre_dominio.[/bold yellow]")
    print("Vamos a añadir algunas reglas...\n")

    reglas.append(addregla(DOMINIO))
    while Prompt.ask("\nQuieres añadir otra? (S)i / (N)o").lower() != "n":
        reglas.append(addregla(DOMINIO))

    append(f"db.{DOMINIO}", reglas)

    printinfo(IP, DOMINIO)


# Inversa
def inversa() -> None:
    print("\n[[bold red blink]![/bold red blink]] Estas añadiendo una regla INdirecta")
    DOMINIO = Prompt.ask(" - Nombre de la zona").lower()
    ip_str = Prompt.ask("Que IP le quieres poner al servidor de DNS? (al derecho)")
    indexes = ([pos for pos, char in enumerate(ip_str) if char == '.'])

    (ip1, ip2, ip3) = (
        ip_str[0:indexes[0]],
        ip_str[indexes[0] + 1:indexes[1]],
        ip_str[indexes[1] + 1:indexes[2]]
    )

    IP = f"{ip3}.{ip2}.{ip1}"

    lines = [
       f"zone \"{IP}.in-addr.arpa\" {'{'}",
        "    type master;",
       f"    file \"{bind_path}/db.{IP}\";",
        "}"
    ]

    append("named.conf.local", lines)

    # crear db.IP
    shutil.copy2(f"{bind_path}/db.127", f"{bind_path}/db.{IP}")

    print(f"[bold][[cyan]INFO[/cyan]] Aqui las reglas son un poco mas xungas, hay que añadir in registro PTR por cada registro A de la zona directa :) [/bold]")

    # editar db.IP
    with open(f"{bind_path}/db.{IP}", "r+") as f:
        filedata = f.read()
        filedata = filedata.replace("1.0.0", "#1.0.0")
        filedata = filedata.replace("localhost", DOMINIO)
        f.seek(0)
        f.write(filedata)
        f.close()

    reglas = []
    reglas.append(addregla(DOMINIO, True))
    while Prompt.ask("\nQuieres añadir otra? (S)i / (N)o").lower() != "n":
        reglas.append(addregla(DOMINIO, True))

    append(f"db.{IP}", reglas)

    print("Se supone que esto lo tienes ya pero...")
    printinfo(IP, DOMINIO)


# Reenviadores
def reenviadores() -> None:
    reenvi = []
    if Prompt.ask("\nQuieres poner los reenviadores del juande ortomatikmente? ([bold blue]S[/bold blue])i / ([bold blue]N[/bold blue])o", choices=["s", "n", "S", "N"], show_choices=False).lower() == "s":
        reenvi = [
            "192.168.8.1",
            "192.168.8.2",
        ]
    else:
        reenvi = []
        reenvi.append(Prompt.ask("IP del reenviador"))
        while Prompt.ask("\nQuieres añadir otro reenviador? (S)i / (N)o", choices=["s", "n", "S", "N"], show_choices=False).lower() != "n":
            reenvi.append(Prompt.ask("IP del reenviador"))
    
    for i, _ in enumerate(reenvi):
        reenvi[i] += ";"

    with open(f"{bind_path}/named.conf.options", "r+") as f:
        filedata = f.read()
        filedata = filedata.replace("// forwarders {", " forwarders {")
        filedata = filedata.replace("// 	0.0.0.0;", "\n\t\t" + '\n\t\t'.join(reenvi))
        filedata = filedata.replace("// };", " };")
        
        f.seek(0)
        f.write(filedata)

        f.seek(0)
        print(f"\n[FILE][bold cyan] named.conf.options[/bold cyan]: \n")
        print(f.read())

        f.close()
        

# Main
ans = Prompt.ask("Que zona quieres hacer?\n([bold blue]D[/bold blue])irecta / ([bold blue]I[/bold blue])nversa / ([bold blue]R[/bold blue])eenviadores").lower()

if ans in ["directa", "d"]:
    directa()
elif ans in ["inversa", "i"]:
    inversa()
elif ans in ["reenviadores", "r"]:
    reenviadores()
