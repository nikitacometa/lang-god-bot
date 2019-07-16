drop table translation;
drop table account;

create table if not exists account(
    user_id int primary key,
    username text not null,
    registered timestamp not null default CURRENT_TIMESTAMP,
    last_quiz timestamp
);

create table if not exists translation(
    user_id int not null references account(user_id),
    source_lang varchar(2) not null check(char_length(source_lang) = 2),
    translation_lang varchar(2) not null check(char_length(translation_lang) = 2),
    word text not null,
    translation text not null,
    added timestamp not null default CURRENT_TIMESTAMP
);
