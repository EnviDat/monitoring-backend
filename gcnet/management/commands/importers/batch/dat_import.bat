cd "path\to\project\directory"

python manage.py dat_import -s test -c config/stations.ini -i gcnet/data/01c.dat -d gcnet/data -m test &
python manage.py dat_import -s 01_swisscamp -c config/stations.ini -i gcnet/data/01c.dat -d gcnet/data -m swisscamp_01d &
python manage.py dat_import -s 02_crawfordpoint -c config/stations.ini -i gcnet/data/02c.dat -d gcnet/data -m crawfordpoint_02d &
python manage.py dat_import -s 03_nasa_u -c config/stations.ini -i gcnet/data/03c.dat -d gcnet/data -m nasa_u_03d &
python manage.py dat_import -s 04_gits -c config/stations.ini -i gcnet/data/04c.dat -d gcnet/data -m gits_04d &
python manage.py dat_import -s 05_humboldt -c config/stations.ini -i gcnet/data/05c.dat -d gcnet/data -m humboldt_05d &
python manage.py dat_import -s 06_summit -c config/stations.ini -i gcnet/data/06c.dat -d gcnet/data -m summit_06d &
python manage.py dat_import -s 07_tunu_n -c config/stations.ini -i gcnet/data/07c.dat -d gcnet/data -m tunu_n_07d &
python manage.py dat_import -s 08_dye2 -c config/stations.ini -i gcnet/data/08c.dat -d gcnet/data -m dye2_08d &
python manage.py dat_import -s 09_jar1 -c config/stations.ini -i gcnet/data/09c.dat -d gcnet/data -m jar1_09d &
python manage.py dat_import -s 10_saddle -c config/stations.ini -i gcnet/data/10c.dat -d gcnet/data -m saddle_10d &
python manage.py dat_import -s 11_southdome -c config/stations.ini -i gcnet/data/11c.dat -d gcnet/data -m southdome_11d &
python manage.py dat_import -s 12_nasa_east -c config/stations.ini -i gcnet/data/12c.dat -d gcnet/data -m nasa_east_12d &
python manage.py dat_import -s 15_nasa_southeast -c config/stations.ini -i gcnet/data/15c.dat -d gcnet/data -m nasa_southeast_15d &
python manage.py dat_import -s 22_petermann -c config/stations.ini -i gcnet/data/22c.dat -d gcnet/data -m petermann_22d &
python manage.py dat_import -s 23_neem -c config/stations.ini -i gcnet/data/23c.dat -d gcnet/data -m neem_23d &
python manage.py dat_import -s 24_east_grip -c config/stations.ini -i gcnet/data/24c.dat -d gcnet/data -m east_grip_24d