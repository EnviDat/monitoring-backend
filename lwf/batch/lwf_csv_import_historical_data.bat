cd "path\to\project\"
CALL .\<venv name>\Scripts\activate.bat

python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/1.csv -t web -d lwf/data -a lwf -m alpthal_bestand_1 -c 1.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/2.csv -t web -d lwf/data -a lwf -m beatenberg_bestand_2 -c 2.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/3.csv -t web -d lwf/data -a lwf -m beatenberg_freiland_3 -c 3.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/4.csv -t web -d lwf/data -a lwf -m bettlachstock_bestand_4 -c 4.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/5.csv -t web -d lwf/data -a lwf -m bettlachstock_freiland_5 -c 5.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/6.csv -t web -d lwf/data -a lwf -m celerina_bestand_6 -c 6.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/7.csv -t web -d lwf/data -a lwf -m celerina_freiland_7 -c 7.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/8.csv -t web -d lwf/data -a lwf -m chironico_bestand_8 -c 8.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/9.csv -t web -d lwf/data -a lwf -m chironico_freiland_9 -c 9.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/12.csv -t web -d lwf/data -a lwf -m isone_bestand_12 -c 12.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/13.csv -t web -d lwf/data -a lwf -m isone_freiland_13 -c 13.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/14.csv -t web -d lwf/data -a lwf -m jussy_bestand_14 -c 14.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/15.csv -t web -d lwf/data -a lwf -m jussy_freiland_15 -c 15.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/18.csv -t web -d lwf/data -a lwf -m lausanne_bestand_18 -c 18.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/19.csv -t web -d lwf/data -a lwf -m lausanne_freiland_19 -c 19.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/20.csv -t web -d lwf/data -a lwf -m lens_bestand_20 -c 20.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/22.csv -t web -d lwf/data -a lwf -m nationalpark_bestand_22 -c 22.csv&
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/23.csv -t web -d lwf/data -a lwf -m nationalpark_freiland_23 -c 23.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/24.csv -t web -d lwf/data -a lwf -m neunkirch_bestand_24 -c 24.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/25.csv -t web -d lwf/data -a lwf -m neunkirch_freiland_25 -c 25.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/26.csv -t web -d lwf/data -a lwf -m novaggio_bestand_26 -c 26.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/27.csv -t web -d lwf/data -a lwf -m novaggio_freiland_27 -c 27.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/28.csv -t web -d lwf/data -a lwf -m othmarsingen_bestand_28 -c 28.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/30.csv -t web -d lwf/data -a lwf -m othmarsingen_freiland_30 -c 30.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/31.csv -t web -d lwf/data -a lwf -m schaenis_bestand_31 -c 31.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/32.csv -t web -d lwf/data -a lwf -m schaenis_freiland_32 -c 32.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/33.csv -t web -d lwf/data -a lwf -m visp_bestand_33 -c 33.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/34.csv -t web -d lwf/data -a lwf -m visp_freiland_34 -c 34.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/35.csv -t web -d lwf/data -a lwf -m vordemwald_bestand_35 -c 35.csv &
python manage.py csv_import -i  https://os.zhdk.cloud.switch.ch/envidat4lwf/p1_meteo/historical/36.csv -t web -d lwf/data -a lwf -m vordemwald_freiland_36 -c 36.csv &
pause
