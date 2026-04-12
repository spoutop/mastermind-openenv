EASY_TEMPLATES = [
    {
        "all_logs": [
            "10:01:00 INFO nginx GET /health 200 12ms",
            "10:01:05 ERROR auth failed_login src=192.168.1.100 user=admin",
            "10:01:10 ERROR auth failed_login src=192.168.1.100 user=admin",
            "10:01:15 ERROR auth failed_login src=192.168.1.100 user=root",
            "10:01:20 ERROR auth failed_login src=192.168.1.100 user=admin",
            "10:02:00 INFO nginx GET /health 200 15ms",
        ],
        "incident": {
            "type": "brute_force", "severity": "high",
            "source_ip": "192.168.1.100", "service": "auth",
        },
        "required_actions": ["query_logs", "block_ip"],
        "correct_targets": {"block_ip": "192.168.1.100"},
        "findings_on_analyze": [
            "source_ip=192.168.1.100 repeated_failed_logins count=4 severity=high",
            "service=auth brute_force_pattern severity=high action_required=block_ip(192.168.1.100)",
        ],
    },
    {
        "all_logs": [
            "09:30:00 INFO api GET /status 200 8ms",
            "09:30:05 ERROR api POST /upload 500 src=10.20.30.40",
            "09:30:10 ERROR api POST /upload 500 src=10.20.30.40",
            "09:30:15 ERROR api POST /upload 500 src=10.20.30.40",
            "09:30:20 WARN disk usage=95% path=/uploads",
            "09:30:25 INFO nginx GET /health 200 10ms",
        ],
        "incident": {
            "type": "resource_exhaustion", "severity": "high",
            "source_ip": "10.20.30.40", "service": "api",
        },
        "required_actions": ["query_logs", "block_ip"],
        "correct_targets": {"block_ip": "10.20.30.40"},
        "findings_on_analyze": [
            "source_ip=10.20.30.40 repeated_upload_failures count=3 severity=high",
            "service=api resource_exhaustion_pattern severity=high action_required=block_ip(10.20.30.40)",
        ],
    },
    {
        "all_logs": [
            "14:00:00 INFO web GET /index 200 20ms",
            "14:00:05 ERROR ssh failed_login src=203.0.113.50 user=root",
            "14:00:10 ERROR ssh failed_login src=203.0.113.50 user=admin",
            "14:00:15 ERROR ssh failed_login src=203.0.113.50 user=deploy",
            "14:00:20 ERROR ssh failed_login src=203.0.113.50 user=root",
            "14:00:30 INFO web GET /index 200 18ms",
        ],
        "incident": {
            "type": "brute_force", "severity": "high",
            "source_ip": "203.0.113.50", "service": "ssh",
        },
        "required_actions": ["query_logs", "block_ip"],
        "correct_targets": {"block_ip": "203.0.113.50"},
        "findings_on_analyze": [
            "source_ip=203.0.113.50 repeated_ssh_failures count=4 severity=high",
            "service=ssh brute_force_pattern severity=high action_required=block_ip(203.0.113.50)",
        ],
    },
]


MEDIUM_TEMPLATES = [
    {
        "all_logs": [
            "10:00:00 INFO api GET /users 200 45ms",
            "10:00:05 WARN api GET /users 200 1200ms",
            "10:00:10 ERROR api GET /users 500 timeout src=10.0.0.55",
            "10:00:15 ERROR api POST /login 500 timeout src=10.0.0.55",
            "10:00:20 WARN db connection_pool exhausted active=50/50",
            "10:00:25 ERROR api GET /users 500 timeout src=10.0.0.55",
            "10:00:30 INFO nginx GET /health 200 10ms",
            "10:00:35 INFO cron backup_job completed",
        ],
        "incident": {
            "type": "dos_attack", "severity": "high",
            "source_ip": "10.0.0.55", "service": "api",
        },
        "required_actions": ["query_logs", "analyze", "block_ip"],
        "correct_targets": {"block_ip": "10.0.0.55"},
        "findings_on_analyze": [
            "source_ip=10.0.0.55 repeated_timeout_errors count=3 severity=high",
            "service=api dos_attack_pattern severity=high action_required=block_ip(10.0.0.55)",
        ],
    },
    {
        "all_logs": [
            "11:00:00 INFO web GET /dashboard 200 30ms",
            "11:00:05 WARN web GET /dashboard 200 2500ms",
            "11:00:10 ERROR web GET /api/data 500 src=172.16.5.99",
            "11:00:15 ERROR web POST /api/data 500 src=172.16.5.99",
            "11:00:20 ERROR web GET /api/data 500 src=172.16.5.99",
            "11:00:25 WARN cache miss_rate=92% service=redis",
            "11:00:30 INFO scheduler job=cleanup status=done",
            "11:00:35 INFO web GET /health 200 12ms",
        ],
        "incident": {
            "type": "dos_attack", "severity": "high",
            "source_ip": "172.16.5.99", "service": "web",
        },
        "required_actions": ["query_logs", "analyze", "block_ip"],
        "correct_targets": {"block_ip": "172.16.5.99"},
        "findings_on_analyze": [
            "source_ip=172.16.5.99 repeated_500_errors count=3 severity=high",
            "service=web dos_attack_pattern severity=high action_required=block_ip(172.16.5.99)",
        ],
    },
    {
        "all_logs": [
            "08:00:00 INFO gateway GET /ping 200 5ms",
            "08:00:05 ERROR auth token_validation_failed src=192.168.50.10",
            "08:00:10 ERROR auth token_validation_failed src=192.168.50.10",
            "08:00:15 WARN auth suspicious_token_reuse src=192.168.50.10",
            "08:00:20 ERROR auth unauthorized_access src=192.168.50.10 path=/admin",
            "08:00:25 INFO monitor memory_usage=45% pid=auth",
            "08:00:30 INFO gateway GET /ping 200 6ms",
            "08:00:35 INFO cron cert_check status=ok",
        ],
        "incident": {
            "type": "token_abuse", "severity": "high",
            "source_ip": "192.168.50.10", "service": "auth",
        },
        "required_actions": ["query_logs", "analyze", "block_ip"],
        "correct_targets": {"block_ip": "192.168.50.10"},
        "findings_on_analyze": [
            "source_ip=192.168.50.10 token_reuse_detected count=3 severity=high",
            "service=auth token_abuse_pattern severity=high action_required=block_ip(192.168.50.10)",
        ],
    },
]


HARD_TEMPLATES = [
    {
        "all_logs": [
            "10:00:00 INFO api GET /health 200 12ms",
            "10:00:05 WARN auth failed_login src=172.16.0.22 user=deploy",
            "10:00:10 ERROR api POST /admin/config 403 src=172.16.0.22",
            "10:00:15 ERROR api POST /admin/users 403 src=172.16.0.22",
            "10:00:20 WARN auth failed_login src=172.16.0.22 user=admin",
            "10:00:25 ERROR api DELETE /admin/logs 403 src=172.16.0.22",
            "10:00:30 INFO cron log_rotate completed",
            "10:00:35 INFO api GET /health 200 14ms",
            "10:00:40 WARN monitor cpu_usage=78% pid=nginx",
            "10:00:45 INFO scheduler job=report_gen status=queued",
        ],
        "incident": {
            "type": "privilege_escalation", "severity": "critical",
            "source_ip": "172.16.0.22", "service": "api",
        },
        "required_actions": ["query_logs", "analyze", "classify", "block_ip"],
        "correct_targets": {"block_ip": "172.16.0.22", "classify": "critical"},
        "findings_on_analyze": [
            "source_ip=172.16.0.22 admin_endpoint_probing count=3 severity=critical",
            "service=api privilege_escalation_attempt severity=critical action_required=classify(critical)+block_ip(172.16.0.22)",
        ],
    },
    {
        "all_logs": [
            "12:00:00 INFO db query_ok table=users 15ms",
            "12:00:05 ERROR db sql_injection_attempt src=10.99.0.1 query=SELECT",
            "12:00:10 ERROR db sql_injection_attempt src=10.99.0.1 query=UNION",
            "12:00:15 WARN db unusual_query_pattern src=10.99.0.1",
            "12:00:20 ERROR db sql_injection_attempt src=10.99.0.1 query=DROP",
            "12:00:25 INFO api GET /health 200 10ms",
            "12:00:30 INFO cron db_backup status=running",
            "12:00:35 INFO monitor disk_usage=55% path=/data",
            "12:00:40 WARN monitor network_latency=120ms dest=cdn",
            "12:00:45 INFO scheduler job=analytics status=queued",
        ],
        "incident": {
            "type": "sql_injection", "severity": "critical",
            "source_ip": "10.99.0.1", "service": "db",
        },
        "required_actions": ["query_logs", "analyze", "classify", "block_ip"],
        "correct_targets": {"block_ip": "10.99.0.1", "classify": "critical"},
        "findings_on_analyze": [
            "source_ip=10.99.0.1 sql_injection_attempts count=3 severity=critical",
            "service=db sql_injection_pattern severity=critical action_required=classify(critical)+block_ip(10.99.0.1)",
        ],
    },
    {
        "all_logs": [
            "15:00:00 INFO web GET /index 200 25ms",
            "15:00:05 ERROR web POST /api/export 500 src=192.168.99.5",
            "15:00:10 ERROR web GET /api/users/dump 403 src=192.168.99.5",
            "15:00:15 WARN web unusual_data_access src=192.168.99.5 volume=500MB",
            "15:00:20 ERROR web GET /api/secrets 403 src=192.168.99.5",
            "15:00:25 INFO nginx GET /health 200 8ms",
            "15:00:30 INFO cron ssl_renewal status=ok",
            "15:00:35 WARN monitor swap_usage=60%",
            "15:00:40 INFO scheduler job=email_digest status=sent",
            "15:00:45 INFO api GET /version 200 5ms",
        ],
        "incident": {
            "type": "data_exfiltration", "severity": "critical",
            "source_ip": "192.168.99.5", "service": "web",
        },
        "required_actions": ["query_logs", "analyze", "classify", "block_ip"],
        "correct_targets": {"block_ip": "192.168.99.5", "classify": "critical"},
        "findings_on_analyze": [
            "source_ip=192.168.99.5 data_exfiltration_attempt volume=500MB severity=critical",
            "service=web unauthorized_data_access severity=critical action_required=classify(critical)+block_ip(192.168.99.5)",
        ],
    },
]


TASK_TEMPLATES = {
    "easy": EASY_TEMPLATES,
    "medium": MEDIUM_TEMPLATES,
    "hard": HARD_TEMPLATES,
}

TASK_CONFIG = {
    "easy": {"max_steps": 5},
    "medium": {"max_steps": 8},
    "hard": {"max_steps": 10},
}
