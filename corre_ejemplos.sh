DIR=codigosDeCurvas
ls $DIR  | while read a
do
   ./mylanga.sh $DIR/$a | gnuplot -p -e "reset; set terminal x11; set label ''; set terminal png; set output '$a.png'; unset key; plot '<cat -' using 1:2 with lines lc rgb 'red'"
done
