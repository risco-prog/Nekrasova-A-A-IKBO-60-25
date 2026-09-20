Задание 2: \
Вывести данные /etc/protocols в отформатированном и отсортированном виде для 5 самых больших портов, как показано в примере ниже: \
[root@localhost etc]# cat /etc/protocols ... \
142 rohc \
141 wesp \
140 shim6 \
139 hip \
138 manet 

Решение: \
cat protocols | cut -f 1,2 | awk '{print $2, $1}' | tail -n 5 | sort -r 

Задача 3 \ 
Написать программу banner средствами bash для вывода текстов, как в следующем примере (размер баннера должен меняться!): 

[root@localhost ~]# ./banner "Hello from RTU MIREA!" \
+-----------------------+ \
| Hello from RTU MIREA! | \
+-----------------------+ 

Решение: \
#!bin/bash \
text="$1" \
len=${#text} \
count=$((len + 2)) \
dashes="" \
for ((i=0; i<count; i++)); do \
dashes="${dashes}-" \
done 

echo "+${dashes}+" \
echo "| $text |" \
echo "+${dashes}+" 


Задача 4
Написать программу для вывода всех идентификаторов (по правилам C/C++ или Java) в файле (без повторений). \
Пример для hello.c: \
h hello include int main n printf return stdio void world 

Решение: \
#!/bin/bash \
file="$1" \
tr -c 'A-Za-z0-9_' '\n' < "$file" \
| grep '^[A-Za-z_][A-Za-z0-9_]*$' \
| tr 'A-Z' 'a-z' | sort -u | tr '\n' ' '

