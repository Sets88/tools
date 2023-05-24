# Upsert
Which doen't increase auto_increment field unlike raw INSERT ... ON DUPLICATE KEY, for cases where most of queries have to update records and just some have to insert

    SET @been_updated=NULL;
    UPDATE some_table SET value='some_data' WHERE name='some_name' AND @been_updated := id;
    INSERT INTO some_table (name, value)
        SELECT 'some_name', 'some_data' WHERE @been_updated IS NULL
    ON DUPLICATE KEY UPDATE value=VALUES(value);

# Debug query using optimizer log

    SET SESSION optimizer_trace="enabled=on";
    SET SESSION optimizer_trace_max_mem_size=100000000;
    <QUERY TO TRACE>
    SELECT TRACE FROM information_schema.optimizer_trace;
