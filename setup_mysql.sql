CREATE DATABASE IF NOT EXISTS skillswap;

CREATE USER IF NOT EXISTS 'skillswap_user'@'localhost'
IDENTIFIED BY 'root';

ALTER USER 'skillswap_user'@'localhost'
IDENTIFIED BY 'root';

GRANT ALL PRIVILEGES ON skillswap.*
TO 'skillswap_user'@'localhost';

FLUSH PRIVILEGES;