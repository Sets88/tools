# Upsert
Which doen't increase auto_increment field unlike raw INSERT ... ON DUPLICATE KEY, for cases where most of queries have to update records and just some have to insert

    SET @been_updated=NULL;
    UPDATE some_table SET value='some_data' WHERE name='some_name' AND @been_updated := id;
    INSERT INTO some_table (name, value)
        SELECT 'some_name', 'some_data' WHERE @been_updated IS NULL
    ON DUPLICATE KEY UPDATE value=VALUES(value);


# Debug the query using the optimizer log

    SET SESSION optimizer_trace="enabled=on";
    SET SESSION optimizer_trace_max_mem_size=100000000;
    <QUERY TO TRACE>
    SELECT TRACE FROM information_schema.optimizer_trace;


# Retrieve all active transactions

    SELECT * FROM information_schema.INNODB_TRX

Use trx_mysql_thread_id to proceed - 1234, this value also may be found in SHOW PROCESSLIST


# Last requests within the transaction

    SELECT t.THREAD_ID, t.PROCESSLIST_ID, t.PROCESSLIST_USER, t.PROCESSLIST_HOST, stmt.TIMER_WAIT, stmt.SQL_TEXT, stmt.CURRENT_SCHEMA
    FROM performance_schema.events_statements_current AS stmt
    INNER JOIN performance_schema.threads AS t ON t.THREAD_ID=stmt.THREAD_ID
    WHERE t.PROCESSLIST_ID=1234


# Get last queries within transaction

    SELECT t.THREAD_ID, t.PROCESSLIST_ID, t.PROCESSLIST_USER, t.PROCESSLIST_HOST, stmt.SQL_TEXT, stmt.CURRENT_SCHEMA
    FROM performance_schema.events_statements_history AS stmt
    LEFT JOIN performance_schema.threads AS t ON performance_schema.stmt.THREAD_ID=t.THREAD_ID
    WHERE t.PROCESSLIST_ID=1234


# All requests pending record lock

    SELECT * FROM sys.innodb_lock_waits


# All requests awaiting table metadata lock

    SELECT * FROM sys.schema_table_lock_waits
