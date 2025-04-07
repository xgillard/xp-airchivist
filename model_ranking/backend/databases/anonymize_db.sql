alter table models 
add alias varchar(30);
------------
update models
set alias = name;
------------
insert into models(name, alias)
values ("A", "gpt4o-mini"),
	   ("B", "llama"),
	   ("C", "mistral7b"),
	   ("D", "mistralnemo"),
	   ("E", "vieille_france"),
	   ("F", "brabant_xvii_ner"),
	   ("G", "vieille_france_v2");
------------
delete from ranking;
------------
update labeling
set model = "A"
where model = "gpt4o-mini";
------------
update labeling
set model = "B"
where model = "llama";
------------
update labeling
set model = "C"
where model = "mistral7b";
------------
update labeling
set model = "D"
where model = "mistralnemo";
------------
update labeling
set model = "E"
where model = "vieille_france";
------------
update labeling
set model = "F"
where model = "brabant_xvii_ner";
------------
update labeling
set model = "G"
where model = "vieille_france_v2";
------------
delete from models 
where name in (
	"gpt4o-mini", 
	"llama", 
	"mistral7b", 
	"mistralnemo", 
	"vieille_france", 
	"brabant_xvii_ner", 
	"vieille_france_v2"
);