# Upsert which doen't increase auto_increment field unlike raw INSERT ... ON DUPLICATE KEY

    SET @been_updated=NULL;
    UPDATE some_table SET value='some_data' WHERE name='some_name' AND @been_updated := id;
    INSERT INTO some_table (name, value)
        SELECT 'some_name', 'some_data' WHERE @been_updated IS NULL
    ON DUPLICATE KEY UPDATE value=VALUES(value);
