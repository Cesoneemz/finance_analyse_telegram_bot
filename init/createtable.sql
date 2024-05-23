CREATE TABLE category
(
    codename VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    aliases TEXT
);

CREATE TABLE expenses
(
    id SERIAL PRIMARY KEY,
    amount INTEGER,
    created_at TIMESTAMP,
    category_codename VARCHAR(255),
    raw_text TEXT,
    FOREIGN KEY(category_codename) REFERENCES category(codename)
);

INSERT INTO category (codename, name, aliases)
VALUES
    ('products', 'продукты', 'еда, продукты питания, супермаркет, покупка продуктов'),
    ('coffee', 'кофе', 'кофейня, старбакс, starbucks, кофе на вынос'),
    ('dinner', 'обед', 'столовая, ланч, бизнес-ланч, бизнес ланч, обеденное время'),
    ('cafe', 'кафе', 'ресторан, рест, мак, макдональдс, макдак, kfc, ilpatio, il patio, бургер кинг, Burger King, subway, сабвей'),
    ('transport', 'общ. транспорт', 'метро, автобус, metro, трамвай, троллейбус, электричка'),
    ('taxi', 'такси', 'яндекс такси, yandex taxi, uber, gett, bolt'),
    ('phone', 'телефон', 'теле2, связь, мегафон, мтс, МТС, билайн, beeline'),
    ('books', 'книги', 'литература, литра, лит-ра, чтение, книжный'),
    ('internet', 'интернет', 'инет, inet, wifi, wi-fi, сеть'),
    ('subscriptions', 'подписки', 'подписка, netflix, youtube premium, spotify, apple music'),
    ('clothing', 'одежда', 'бутик, магазин одежды, шопинг, одежда'),
    ('health', 'здоровье', 'аптека, лекарства, врач, поликлиника, больница'),
    ('entertainment', 'развлечения', 'кино, театр, концерт, музей, парк, аттракционы'),
    ('beauty', 'красота', 'салон, парикмахерская, маникюр, спа, косметика'),
    ('fitness', 'фитнес', 'спортзал, тренажерный зал, йога, пилатес, фитнес клуб'),
    ('travel', 'путешествия', 'туры, билеты, отель, проживание, авиабилеты, поезда'),
    ('other', 'прочее', '');

