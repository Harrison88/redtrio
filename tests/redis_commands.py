# flake8: noqa
from redtrio.lowlevel.protocol import RedisError

redis_commands = {
    b"HELLO 3": {
        "encoded": b"*2\r\n$5\r\nHELLO\r\n$1\r\n3\r\n",
        "response": b"%7\r\n$6\r\nserver\r\n$5\r\nredis\r\n$7\r\nversion\r\n$5\r\n6.0.5\r\n$5\r\nproto\r\n:3\r\n$2\r\nid\r\n:628\r\n$4\r\nmode\r\n$10\r\nstandalone\r\n$4\r\nrole\r\n$6\r\nmaster\r\n$7\r\nmodules\r\n*0\r\n",
        "response_value": {
            b"server": b"redis",
            b"version": b"6.0.5",
            b"proto": 3,
            b"id": 628,
            b"mode": b"standalone",
            b"role": b"master",
            b"modules": [],
        },
    },
    b"PING": {
        "encoded": b"*1\r\n$4\r\nPING\r\n",
        "response": b"+PONG\r\n",
        "response_value": b"PONG",
    },
    b"SET foo bar": {
        "encoded": b"*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n",
        "response": b"+OK\r\n",
        "response_value": b"OK",
    },
    b"GET foo": {
        "encoded": b"*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n",
        "response": b"$3\r\nbar\r\n",
        "response_value": b"bar",
    },
    b"MSET language Python version 3": {
        "encoded": b"*5\r\n$4\r\nMSET\r\n$8\r\nlanguage\r\n$6\r\nPython\r\n$7\r\nversion\r\n$1\r\n3\r\n",
        "response": b"+OK\r\n",
        "response_value": b"OK",
    },
    b"MGET language version": {
        "encoded": b"*3\r\n$4\r\nMGET\r\n$8\r\nlanguage\r\n$7\r\nversion\r\n",
        "response": b"*2\r\n$6\r\nPython\r\n$1\r\n3\r\n",
        "response_value": [b"Python", b"3"],
    },
    b"NOT A COMMAND": {
        "encoded": b"*3\r\n$3\r\nNOT\r\n$1\r\nA\r\n$7\r\nCOMMAND\r\n",
        "response": b"-ERR unknown command `NOT`, with args beginning with: `A`, `COMMAND`, \r\n",
        "response_value": RedisError(
            b"ERR", b"unknown command `NOT`, with args beginning with: `A`, `COMMAND`, "
        ),
    },
    b"GET nonexistent": {
        "encoded": b"*2\r\n$3\r\nGET\r\n$11\r\nnonexistant\r\n",
        "response": b"_\r\n",
        "response_value": None,
    },
    b"ZADD myset 1.2 foo": {
        "encoded": b"*4\r\n$4\r\nZADD\r\n$5\r\nmyset\r\n$3\r\n1.2\r\n$3\r\nfoo\r\n",
        "response": b":1\r\n",
        "response_value": 1,
    },
    b"ZSCORE myset foo": {
        "encoded": b"*3\r\n$6\r\nZSCORE\r\n$5\r\nmyset\r\n$3\r\nfoo\r\n",
        "response": b",1.2\r\n",
        "response_value": 1.2,
    },
    b"INFO": {
        "encoded": b"*1\r\n$4\r\nINFO\r\n",
        "response": b"=3584\r\ntxt:# Server\r\nredis_version:6.0.5\r\nredis_git_sha1:51efb7fe\r\nredis_git_dirty:0\r\nredis_build_id:39ec5b348af7f138\r\nredis_mode:standalone\r\nos:Linux 5.6.8-200.fc31.x86_64 x86_64\r\narch_bits:64\r\nmultiplexing_api:epoll\r\natomicvar_api:atomic-builtin\r\ngcc_version:9.3.1\r\nprocess_id:289897\r\nrun_id:8c8cd073d48b325ad101adc30575e25b88efb582\r\ntcp_port:6379\r\nuptime_in_seconds:13820\r\nuptime_in_days:0\r\nhz:10\r\nconfigured_hz:10\r\nlru_clock:16749320\r\nexecutable:/home/harrison/Programming/open_source/redis/src/./redis-server\r\nconfig_file:\r\n\r\n# Clients\r\nconnected_clients:1\r\nclient_recent_max_input_buffer:4\r\nclient_recent_max_output_buffer:0\r\nblocked_clients:0\r\ntracking_clients:0\r\nclients_in_timeout_table:0\r\n\r\n# Memory\r\nused_memory:866664\r\nused_memory_human:846.35K\r\nused_memory_rss:5455872\r\nused_memory_rss_human:5.20M\r\nused_memory_peak:1892088\r\nused_memory_peak_human:1.80M\r\nused_memory_peak_perc:45.80%\r\nused_memory_overhead:820050\r\nused_memory_startup:802872\r\nused_memory_dataset:46614\r\nused_memory_dataset_perc:73.07%\r\nallocator_allocated:1580200\r\nallocator_active:2019328\r\nallocator_resident:4444160\r\ntotal_system_memory:8246517760\r\ntotal_system_memory_human:7.68G\r\nused_memory_lua:37888\r\nused_memory_lua_human:37.00K\r\nused_memory_scripts:0\r\nused_memory_scripts_human:0B\r\nnumber_of_cached_scripts:0\r\nmaxmemory:0\r\nmaxmemory_human:0B\r\nmaxmemory_policy:noeviction\r\nallocator_frag_ratio:1.28\r\nallocator_frag_bytes:439128\r\nallocator_rss_ratio:2.20\r\nallocator_rss_bytes:2424832\r\nrss_overhead_ratio:1.23\r\nrss_overhead_bytes:1011712\r\nmem_fragmentation_ratio:6.62\r\nmem_fragmentation_bytes:4631712\r\nmem_not_counted_for_evict:0\r\nmem_replication_backlog:0\r\nmem_clients_slaves:0\r\nmem_clients_normal:16986\r\nmem_aof_buffer:0\r\nmem_allocator:jemalloc-5.1.0\r\nactive_defrag_running:0\r\nlazyfree_pending_objects:0\r\n\r\n# Persistence\r\nloading:0\r\nrdb_changes_since_last_save:0\r\nrdb_bgsave_in_progress:0\r\nrdb_last_save_time:1593805524\r\nrdb_last_bgsave_status:ok\r\nrdb_last_bgsave_time_sec:0\r\nrdb_current_bgsave_time_sec:-1\r\nrdb_last_cow_size:278528\r\naof_enabled:0\r\naof_rewrite_in_progress:0\r\naof_rewrite_scheduled:0\r\naof_last_rewrite_time_sec:-1\r\naof_current_rewrite_time_sec:-1\r\naof_last_bgrewrite_status:ok\r\naof_last_write_status:ok\r\naof_last_cow_size:0\r\nmodule_fork_in_progress:0\r\nmodule_fork_last_cow_size:0\r\n\r\n# Stats\r\ntotal_connections_received:508\r\ntotal_commands_processed:47\r\ninstantaneous_ops_per_sec:0\r\ntotal_net_input_bytes:1418\r\ntotal_net_output_bytes:44357\r\ninstantaneous_input_kbps:0.00\r\ninstantaneous_output_kbps:0.00\r\nrejected_connections:0\r\nsync_full:0\r\nsync_partial_ok:0\r\nsync_partial_err:0\r\nexpired_keys:0\r\nexpired_stale_perc:0.00\r\nexpired_time_cap_reached_count:0\r\nexpire_cycle_cpu_milliseconds:382\r\nevicted_keys:0\r\nkeyspace_hits:7\r\nkeyspace_misses:7\r\npubsub_channels:0\r\npubsub_patterns:0\r\nlatest_fork_usec:225\r\nmigrate_cached_sockets:0\r\nslave_expires_tracked_keys:0\r\nactive_defrag_hits:0\r\nactive_defrag_misses:0\r\nactive_defrag_key_hits:0\r\nactive_defrag_key_misses:0\r\ntracking_total_keys:0\r\ntracking_total_items:0\r\ntracking_total_prefixes:0\r\nunexpected_error_replies:0\r\n\r\n# Replication\r\nrole:master\r\nconnected_slaves:0\r\nmaster_replid:b95f762ca2b3ac644906b8d821596d2a6b4b52fa\r\nmaster_replid2:0000000000000000000000000000000000000000\r\nmaster_repl_offset:0\r\nsecond_repl_offset:-1\r\nrepl_backlog_active:0\r\nrepl_backlog_size:1048576\r\nrepl_backlog_first_byte_offset:0\r\nrepl_backlog_histlen:0\r\n\r\n# CPU\r\nused_cpu_sys:11.151802\r\nused_cpu_user:12.467941\r\nused_cpu_sys_children:0.003669\r\nused_cpu_user_children:0.001012\r\n\r\n# Modules\r\n\r\n# Cluster\r\ncluster_enabled:0\r\n\r\n# Keyspace\r\ndb0:keys=4,expires=0,avg_ttl=0\r\n\r\n",
        "response_value": b"# Server\r\nredis_version:6.0.5\r\nredis_git_sha1:51efb7fe\r\nredis_git_dirty:0\r\nredis_build_id:39ec5b348af7f138\r\nredis_mode:standalone\r\nos:Linux 5.6.8-200.fc31.x86_64 x86_64\r\narch_bits:64\r\nmultiplexing_api:epoll\r\natomicvar_api:atomic-builtin\r\ngcc_version:9.3.1\r\nprocess_id:289897\r\nrun_id:8c8cd073d48b325ad101adc30575e25b88efb582\r\ntcp_port:6379\r\nuptime_in_seconds:13820\r\nuptime_in_days:0\r\nhz:10\r\nconfigured_hz:10\r\nlru_clock:16749320\r\nexecutable:/home/harrison/Programming/open_source/redis/src/./redis-server\r\nconfig_file:\r\n\r\n# Clients\r\nconnected_clients:1\r\nclient_recent_max_input_buffer:4\r\nclient_recent_max_output_buffer:0\r\nblocked_clients:0\r\ntracking_clients:0\r\nclients_in_timeout_table:0\r\n\r\n# Memory\r\nused_memory:866664\r\nused_memory_human:846.35K\r\nused_memory_rss:5455872\r\nused_memory_rss_human:5.20M\r\nused_memory_peak:1892088\r\nused_memory_peak_human:1.80M\r\nused_memory_peak_perc:45.80%\r\nused_memory_overhead:820050\r\nused_memory_startup:802872\r\nused_memory_dataset:46614\r\nused_memory_dataset_perc:73.07%\r\nallocator_allocated:1580200\r\nallocator_active:2019328\r\nallocator_resident:4444160\r\ntotal_system_memory:8246517760\r\ntotal_system_memory_human:7.68G\r\nused_memory_lua:37888\r\nused_memory_lua_human:37.00K\r\nused_memory_scripts:0\r\nused_memory_scripts_human:0B\r\nnumber_of_cached_scripts:0\r\nmaxmemory:0\r\nmaxmemory_human:0B\r\nmaxmemory_policy:noeviction\r\nallocator_frag_ratio:1.28\r\nallocator_frag_bytes:439128\r\nallocator_rss_ratio:2.20\r\nallocator_rss_bytes:2424832\r\nrss_overhead_ratio:1.23\r\nrss_overhead_bytes:1011712\r\nmem_fragmentation_ratio:6.62\r\nmem_fragmentation_bytes:4631712\r\nmem_not_counted_for_evict:0\r\nmem_replication_backlog:0\r\nmem_clients_slaves:0\r\nmem_clients_normal:16986\r\nmem_aof_buffer:0\r\nmem_allocator:jemalloc-5.1.0\r\nactive_defrag_running:0\r\nlazyfree_pending_objects:0\r\n\r\n# Persistence\r\nloading:0\r\nrdb_changes_since_last_save:0\r\nrdb_bgsave_in_progress:0\r\nrdb_last_save_time:1593805524\r\nrdb_last_bgsave_status:ok\r\nrdb_last_bgsave_time_sec:0\r\nrdb_current_bgsave_time_sec:-1\r\nrdb_last_cow_size:278528\r\naof_enabled:0\r\naof_rewrite_in_progress:0\r\naof_rewrite_scheduled:0\r\naof_last_rewrite_time_sec:-1\r\naof_current_rewrite_time_sec:-1\r\naof_last_bgrewrite_status:ok\r\naof_last_write_status:ok\r\naof_last_cow_size:0\r\nmodule_fork_in_progress:0\r\nmodule_fork_last_cow_size:0\r\n\r\n# Stats\r\ntotal_connections_received:508\r\ntotal_commands_processed:47\r\ninstantaneous_ops_per_sec:0\r\ntotal_net_input_bytes:1418\r\ntotal_net_output_bytes:44357\r\ninstantaneous_input_kbps:0.00\r\ninstantaneous_output_kbps:0.00\r\nrejected_connections:0\r\nsync_full:0\r\nsync_partial_ok:0\r\nsync_partial_err:0\r\nexpired_keys:0\r\nexpired_stale_perc:0.00\r\nexpired_time_cap_reached_count:0\r\nexpire_cycle_cpu_milliseconds:382\r\nevicted_keys:0\r\nkeyspace_hits:7\r\nkeyspace_misses:7\r\npubsub_channels:0\r\npubsub_patterns:0\r\nlatest_fork_usec:225\r\nmigrate_cached_sockets:0\r\nslave_expires_tracked_keys:0\r\nactive_defrag_hits:0\r\nactive_defrag_misses:0\r\nactive_defrag_key_hits:0\r\nactive_defrag_key_misses:0\r\ntracking_total_keys:0\r\ntracking_total_items:0\r\ntracking_total_prefixes:0\r\nunexpected_error_replies:0\r\n\r\n# Replication\r\nrole:master\r\nconnected_slaves:0\r\nmaster_replid:b95f762ca2b3ac644906b8d821596d2a6b4b52fa\r\nmaster_replid2:0000000000000000000000000000000000000000\r\nmaster_repl_offset:0\r\nsecond_repl_offset:-1\r\nrepl_backlog_active:0\r\nrepl_backlog_size:1048576\r\nrepl_backlog_first_byte_offset:0\r\nrepl_backlog_histlen:0\r\n\r\n# CPU\r\nused_cpu_sys:11.151802\r\nused_cpu_user:12.467941\r\nused_cpu_sys_children:0.003669\r\nused_cpu_user_children:0.001012\r\n\r\n# Modules\r\n\r\n# Cluster\r\ncluster_enabled:0\r\n\r\n# Keyspace\r\ndb0:keys=4,expires=0,avg_ttl=0\r\n",
    },
    b"SADD a_set super_value": {
        "encoded": b"*3\r\n$4\r\nSADD\r\n$5\r\na_set\r\n$11\r\nsuper_value\r\n",
        "response": b":1\r\n",
        "response_value": 1,
    },
    b"SMEMBERS a_set": {
        "encoded": b"*2\r\n$8\r\nSMEMBERS\r\n$5\r\na_set\r\n",
        "response": b"~1\r\n$11\r\nsuper_value\r\n",
        "response_value": {b"super_value"},
    },
}
