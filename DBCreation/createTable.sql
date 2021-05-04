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

CREATE TABLE super_mario.Livello1Goomba (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello1Koopa (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello1Coin (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello1Checkpoint (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello1Door (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello1Powerup (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello2Goomba (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello2Koopa (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello2Coin (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello2Checkpoint (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello2Door (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello2Powerup (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello3Goomba (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello3Koopa (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello3Coin (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello3Checkpoint (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello3Door (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello3Powerup (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello4Goomba (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello4Koopa (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello4Coin (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello4Checkpoint (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello4Door (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello4Powerup (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL
);

CREATE TABLE super_mario.Livello4Platform (
	id INT PRIMARY KEY AUTO_INCREMENT,
	center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    boundary_left FLOAT NOT NULL,
	boundary_right FLOAT NOT NULL,
    speed FLOAT NOT NULL
);