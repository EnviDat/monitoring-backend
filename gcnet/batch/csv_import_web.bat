cd "path\to\project\directory"

python manage.py csv_import -s 00_swisscamp_10m -c config/stations.ini -i https://www.wsl.ch/gcnet/data/0.csv -d gcnet/data -m swisscamp_10m_tower_00d -t web &
python manage.py csv_import -s 01_swisscamp -c config/stations.ini -i https://www.wsl.ch/gcnet/data/1.csv -d gcnet/data -m swisscamp_01d -t web &
python manage.py csv_import -s 02_crawfordpoint -c config/stations.ini -i https://www.wsl.ch/gcnet/data/2.csv -d gcnet/data -m crawfordpoint_02d -t web &
python manage.py csv_import -s 03_nasa_u -c config/stations.ini -i https://www.wsl.ch/gcnet/data/3.csv -d gcnet/data -m nasa_u_03d -t web &
python manage.py csv_import -s 04_gits -c config/stations.ini -i https://www.wsl.ch/gcnet/data/4.csv -d gcnet/data -m gits_04d -t web &
python manage.py csv_import -s 05_humboldt -c config/stations.ini -i https://www.wsl.ch/gcnet/data/5.csv -d gcnet/data -m humboldt_05d -t web &
python manage.py csv_import -s 06_summit -c config/stations.ini -i https://www.wsl.ch/gcnet/data/6.csv -d gcnet/data -m summit_06d -t web &
python manage.py csv_import -s 07_tunu_n -c config/stations.ini -i https://www.wsl.ch/gcnet/data/7.csv -d gcnet/data -m tunu_n_07d -t web &
python manage.py csv_import -s 08_dye2 -c config/stations.ini -i https://www.wsl.ch/gcnet/data/8.csv -d gcnet/data -m dye2_08d -t web &
python manage.py csv_import -s 09_jar1 -c config/stations.ini -i https://www.wsl.ch/gcnet/data/9.csv -d gcnet/data -m jar1_09d -t web &
python manage.py csv_import -s 10_saddle -c config/stations.ini -i https://www.wsl.ch/gcnet/data/10.csv -d gcnet/data -m saddle_10d -t web &
python manage.py csv_import -s 11_southdome -c config/stations.ini -i https://www.wsl.ch/gcnet/data/11.csv -d gcnet/data -m southdome_11d -t web &
python manage.py csv_import -s 12_nasa_east -c config/stations.ini -i https://www.wsl.ch/gcnet/data/12.csv -d gcnet/data -m nasa_east_12d -t web &
python manage.py csv_import -s 22_petermann -c config/stations.ini -i https://www.wsl.ch/gcnet/data/22.csv -d gcnet/data -m petermann_22d -t web &
python manage.py csv_import -s 23_neem -c config/stations.ini -i https://www.wsl.ch/gcnet/data/23.csv -d gcnet/data -m neem_23d -t web &
python manage.py csv_import -s 24_east_grip -c config/stations.ini -i https://www.wsl.ch/gcnet/data/24.csv -d gcnet/data -m east_grip_24d -t web