-- CS350 Assignment 5

-- Question 1
-- Number of rows produced 54 records: 
SELECT book_title, reader_rating, year_published
FROM Book
ORDER BY reader_rating DESC;


-- Question 2
-- Number of rows produced 17 records: 

SELECT book_title, sales_revenue
FROM Book
WHERE sales_revenue > 500
ORDER BY sales_revenue DESC, book_title ASC;


-- Question 3
-- Number of rows produced  8 records: 
SELECT book_title, reader_rating
FROM Book
WHERE book_title LIKE '%Harbor%'
    OR book_title LIKE '%Kingdom%'
ORDER BY reader_rating DESC;

-- Question 4
-- Number of rows produced  15 records: 
SELECT book_title AS "Book Title", reader_rating AS "Reader Rating", year_published AS "Year Published"
FROM Book
WHERE year_published < 2020 AND reader_rating >= 8.5
ORDER BY reader_rating DESC, year_published ASC;

-- Question 5
-- Number of rows produced  32 records: 
SELECT book_title, year_published
FROM Book
WHERE year_published BETWEEN 2020 AND 2024
ORDER BY year_published DESC;

-- Question 6
-- Number of rows produced 9 records: 
SELECT genre, COUNT(*) AS "Book-Count"
FROM Book
GROUP BY genre
ORDER BY "Book-Count" DESC;

-- Question 7
-- Number of rows produced 39 records: 
SELECT year_published, genre, COUNT(*) AS "Book-Count"
FROM Book
GROUP BY year_published, genre
ORDER BY year_published ASC, genre ASC;

-- Question 8
-- Number of rows produced 54 records: 
SELECT Book.book_title, Publisher.publisher_name
FROM Book
JOIN Publisher
ON Book.publisher_id = Publisher.id
ORDER BY Book.book_title ASC;

-- Question 9
-- Number of rows produced  13 records: 
-- Question 9
-- Number of rows produced: 13 records
SELECT Publisher.publisher_name,
       ROUND(AVG(Book.reader_rating), 1) AS "Average Reader Rating"
FROM Publisher
JOIN Book
ON Publisher.id = Book.publisher_id
GROUP BY Publisher.publisher_name
ORDER BY "Average Reader Rating" DESC,
         Publisher.publisher_name ASC;
         
-- Question 10
-- Number of rows produced 8 records: 
SELECT Publisher.publisher_name,
       ROUND(AVG(Book.sales_revenue), 0) AS "Average Sales Revenue"
FROM Publisher
JOIN Book
ON Publisher.id = Book.publisher_id
GROUP BY Publisher.publisher_name
HAVING AVG(Book.sales_revenue) > 300
ORDER BY ROUND(AVG(Book.sales_revenue), 0) DESC,
         Publisher.publisher_name ASC;

-- Question 11
-- Number of rows produced 35 records: 
SELECT Book.book_title, Book.reader_rating, Publisher.publisher_name
FROM BOOK
JOIN Publisher
ON Publisher.id = Book.publisher_id
WHERE Book.reader_rating > 8.0
ORDER BY Book.reader_rating DESC,
    Book.book_title ASC;

-- Question 12
-- Number of rows produced 13 records: 
SELECT Publisher.publisher_name, SUM(Book.sales_revenue) AS "Total Sales Revenue"
FROM Publisher
JOIN BOOK
ON Publisher.id = Book.publisher_id
GROUP BY Publisher.publisher_name;