
## movies
Изменения по сравнению с базовой схемой урока:  
(#убрал поле id - зачем оно?) - не убрал пока :)  
rars_rating типа byte хранит число {0, 6, 12, 18} (без +)
Возрастная классификация информационной продукции (Russian Age Rating System, RARS
0+, 6+, 12+, 16+, 18+
fw_type - тип кинопроизведения: фильм или сериал

* imdb_rating: float
* rars_rating: byte (0, 6, 12, 16, 18)
* fw_type: keyword (movie | tv show) 

* genre: keyword
* genres:  [{id: keyword, name: text}]

* title: text
* description: text
        
* directors_names: text
* actors_names: text
* writers_names: text
        
* actors: [{id: keyword, name: text}]
* writers: [{id: keyword, name: text}]
* directors: [{id: keyword, name: text}]
    


## genres
* name: keyword

## persons
* full_name: text
 