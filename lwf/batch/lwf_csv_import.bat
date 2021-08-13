cd "path\to\project\"
CALL .\<venv name>\Scripts\activate.bat

python manage.py csv_import -i lwf/data/1.csv -t directory -d lwf/data -a lwf -m alpthal_bestand_1 &
python manage.py csv_import -i lwf/data/2.csv -t directory -d lwf/data -a lwf -m beatenberg_bestand_2 &
python manage.py csv_import -i lwf/data/3.csv -t directory -d lwf/data -a lwf -m beatenberg_freiland_3 &
python manage.py csv_import -i lwf/data/4.csv -t directory -d lwf/data -a lwf -m bettlachstock_bestand_4 &
python manage.py csv_import -i lwf/data/5.csv -t directory -d lwf/data -a lwf -m bettlachstock_freiland_5 &
python manage.py csv_import -i lwf/data/6.csv -t directory -d lwf/data -a lwf -m celerina_bestand_6 &
python manage.py csv_import -i lwf/data/7.csv -t directory -d lwf/data -a lwf -m celerina_freiland_7 &
python manage.py csv_import -i lwf/data/8.csv -t directory -d lwf/data -a lwf -m chironico_bestand_8 &
python manage.py csv_import -i lwf/data/9.csv -t directory -d lwf/data -a lwf -m chironico_freiland_9 &
python manage.py csv_import -i lwf/data/12.csv -t directory -d lwf/data -a lwf -m isone_bestand_12 &
python manage.py csv_import -i lwf/data/13.csv -t directory -d lwf/data -a lwf -m isone_freiland_13 &
python manage.py csv_import -i lwf/data/14.csv -t directory -d lwf/data -a lwf -m jussy_bestand_14 &
python manage.py csv_import -i lwf/data/15.csv -t directory -d lwf/data -a lwf -m jussy_freiland_15 &
python manage.py csv_import -i lwf/data/18.csv -t directory -d lwf/data -a lwf -m lausanne_bestand_18 &
python manage.py csv_import -i lwf/data/19.csv -t directory -d lwf/data -a lwf -m lausanne_freiland_19 &
python manage.py csv_import -i lwf/data/20.csv -t directory -d lwf/data -a lwf -m lens_bestand_20 &
python manage.py csv_import -i lwf/data/22.csv -t directory -d lwf/data -a lwf -m nationalpark_bestand_22 &
python manage.py csv_import -i lwf/data/23.csv -t directory -d lwf/data -a lwf -m nationalpark_freiland_23 &
python manage.py csv_import -i lwf/data/24.csv -t directory -d lwf/data -a lwf -m neunkirch_bestand_24 &
python manage.py csv_import -i lwf/data/25.csv -t directory -d lwf/data -a lwf -m neunkirch_freiland_25 &
python manage.py csv_import -i lwf/data/26.csv -t directory -d lwf/data -a lwf -m novaggio_bestand_26 &
python manage.py csv_import -i lwf/data/27.csv -t directory -d lwf/data -a lwf -m novaggio_freiland_27 &
python manage.py csv_import -i lwf/data/28.csv -t directory -d lwf/data -a lwf -m othmarsingen_bestand_28 &
python manage.py csv_import -i lwf/data/30.csv -t directory -d lwf/data -a lwf -m othmarsingen_freiland_30 &
python manage.py csv_import -i lwf/data/31.csv -t directory -d lwf/data -a lwf -m schaenis_bestand_31 &
python manage.py csv_import -i lwf/data/32.csv -t directory -d lwf/data -a lwf -m schaenis_freiland_32 &
python manage.py csv_import -i lwf/data/33.csv -t directory -d lwf/data -a lwf -m visp_bestand_33 &
python manage.py csv_import -i lwf/data/34.csv -t directory -d lwf/data -a lwf -m visp_freiland_34 &
python manage.py csv_import -i lwf/data/35.csv -t directory -d lwf/data -a lwf -m vordemwald_bestand_35 &
python manage.py csv_import -i lwf/data/36.csv -t directory -d lwf/data -a lwf -m vordemwald_freiland_36 &
pause
