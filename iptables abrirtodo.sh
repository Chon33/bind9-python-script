#!/bin/sh
## SCRIPT de IPTABLES –PERMITE ACCEDER A INTERNET A LA RED

red=""

echo -n Aplicando Reglas de Firewall...

## INICIALIZACIÓN
iptables -F
iptables -X
iptables -Z
iptables -t nat -F

## Establecemos politica por defecto ACEPTAR
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -t nat -P PREROUTING ACCEPT
iptables -t nat -P POSTROUTING ACCEPT

iptables -t nat -A POSTROUTING -s $red -o enp0s8 -j MASQUERADE

#Activar forwarding (reenvío de paquetes)
echo 1 > /proc/sys/net/ipv4/ip_forward

echo " OK . Verifique que lo que se aplica con: iptables -L -n"
# Fin del script
