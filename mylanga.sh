(cd $(dirname $0);rm -f parse*)

if [ $# -gt 1 ]; then
   echo "Uso: $0 [archivo de entrada]" >&2
   exit 1
else
   if [ $# -eq 1 ]; then
      if [ -f $1 ]; then
         (cd $(dirname $0);python mylanga.py) < $1
      else
         echo "El archivo $1 no existe" >&2
         exit 1
      fi
   else 
      (cd $(dirname $0);python mylanga.py)
   fi
fi
