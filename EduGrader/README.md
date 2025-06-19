# EduGrader

**Requirements for running the project:**
<p></p>
pip install -r requirements.txt


<p></p>
**For databases:(MySql)**
<p></p>
CREATE DATABASE edugrader;
<p></p>
USE edugrader;

CREATE TABLE user (
    id INT PRIMARY KEY,
    username varchar(50),
    password varchar(50),
    email varchar(50)
);

create table history(
	qno int primary key,
    question varchar(1500),
    answer varchar(1500),
    feedback varchar(1500),
    marks int
);

ALTER TABLE history ADD COLUMN user_id INT;

ALTER TABLE history
ADD CONSTRAINT fk_user_id
FOREIGN KEY (user_id) REFERENCES user(id);

select *  from user;

select * from history;
