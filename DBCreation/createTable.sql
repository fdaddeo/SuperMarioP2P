CREATE DATABASE super_mario;

CREATE TABLE super_mario.singleplayer_record (
	id INT PRIMARY KEY AUTO_INCREMENT,
	player_name CHAR(3) NOT NULL,
    	total_time FLOAT NOT NULL,
   	lives INT NOT NULL,
    	date_played DATE NOT NULL
);

CREATE TABLE super_mario.multiplayer_record (
	id INT PRIMARY KEY AUTO_INCREMENT,
	player_name CHAR(3) NOT NULL,
    	total_time FLOAT NOT NULL,
    	lives INT NOT NULL,
    	date_played DATE NOT NULL
);

CREATE TABLE super_mario.livello1goomba (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);

CREATE TABLE super_mario.livello1koopa (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);

CREATE TABLE super_mario.livello1coin (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello1checkpoint (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello1door (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello1powerup (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello2goomba (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);

CREATE TABLE super_mario.livello2koopa (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);

CREATE TABLE super_mario.livello2coin (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello2checkpoint (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello2door (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello2powerup (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello3goomba (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);

CREATE TABLE super_mario.livello3koopa (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);

CREATE TABLE super_mario.livello3coin (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello3checkpoint (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello3door (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello3powerup (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello4goomba (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);

CREATE TABLE super_mario.livello4koopa (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);

CREATE TABLE super_mario.livello4coin (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello4checkpoint (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello4door (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
   	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello4powerup (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.livello4platform (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    	center_y FLOAT NOT NULL,
    	boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    	speed FLOAT NOT NULL
);
