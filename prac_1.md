# Задание 2:
Вывести данные /etc/protocols в отформатированном и отсортированном виде для 5 самых больших портов, как показано в примере ниже: \
[root@localhost etc]# cat /etc/protocols ... \
142 rohc \
141 wesp \
140 shim6 \
139 hip \
138 manet 

## Решение: 
```
cat protocols | cut -f 1,2 | awk '{print $2, $1}' | tail -n 5 | sort -r
```

# Задача 3 
Написать программу banner средствами bash для вывода текстов, как в следующем примере (размер баннера должен меняться!): 

[root@localhost ~]# ./banner "Hello from RTU MIREA!" \
+-----------------------+ \
| Hello from RTU MIREA! | \
+-----------------------+ 

## Решение: 
```
#!/bin/bash 
text="$1" 
len=${#text} 
count=$((len + 2)) 
dashes="" 
for ((i=0; i<count; i++)); do 
dashes="${dashes}-" 
done 

echo "+${dashes}+" 
echo "| $text |" 
echo "+${dashes}+" 
```

# Задача 4
Написать программу для вывода всех идентификаторов (по правилам C/C++ или Java) в файле (без повторений). \
Пример для hello.c: \
h hello include int main n printf return stdio void world 

## Решение: 
```
#!/bin/bash 
file="$1" 
tr -c 'A-Za-z0-9_' '\n' < "$file" |
grep '^[A-Za-z_][A-Za-z0-9_]*$' |
sort -u | tr '\n' ' '
```
# Задача 5
Написать программу для регистрации пользовательской команды (правильные права доступа и копирование в /usr/local/bin). 

Например, пусть программа называется reg:

./reg banner

# Решение 
```
#!/bin/bash

file="$1"

chmod +x "$file"
sudo cp "$file" /usr/local/bin/ 
```
# Задача 6
Написать программу для проверки наличия комментария в первой строке файлов с расширением c, js и py.

# Решение 
```
#!/bin/bash

for file in "$1"/*.{c,js,py}
do
    if [ -f "$file" ]; then
        first=$(head -n 1 "$file")

        case "$file" in
            *.py)
                if [[ "$first" == \#* ]]; then
                    echo "$file: comment found"
                else
                    echo "$file: comment not found"
                fi
                ;;
            *.c|*.js)
                if [[ "$first" == //* ]]; then
                    echo "$file: comment found"
                else
                    echo "$file: comment not found"
                fi
                ;;
        esac
    fi
done
```

# Задача 7
Написать программу для нахождения файлов-дубликатов (имеющих 1 или более копий содержимого) по заданному пути (и подкаталогам).

# Решение 
```
#!/bin/bash

find "$1" -type f -exec md5sum {} + | sort |
while read -r hash file
do
    if [ "$hash" = "$previous_hash" ]; then
        echo "Duplicate: $previous_file"
        echo "Duplicate: $file"
        echo
    fi

    previous_hash="$hash"
    previous_file="$file"
done
```

# Задача 8
Написать программу, которая находит все файлы в данном каталоге с расширением, указанным в качестве аргумента и архивирует все эти файлы в архив tar.

# Решение 
```
#!/bin/bash

directory="$1"
extension="$2"

find "$directory" -type f -name "*.$extension" > files.txt

tar -cf archive.tar -T files.txt

rm files.txt

echo "Archive created: archive.tar"
```

# Задача 9
Написать программу, которая заменяет в файле последовательности из 4 пробелов на символ табуляции. Входной и выходной файлы задаются аргументами.

# Решение 
```
#!/bin/bash

input="$1"
output="$2"

sed 's/    /\t/g' "$input" > "$output"

echo "File converted"
```

# Задача 10
Написать программу, которая выводит названия всех пустых текстовых файлов в указанной директории. Директория передается в программу параметром.

# Решение 
```
#!/bin/bash

find "$1" -type f -empty -name "*.txt"
```
