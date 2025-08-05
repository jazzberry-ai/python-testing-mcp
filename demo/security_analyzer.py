"""
Security analysis and validation framework for defensive security testing.
Demonstrates complex validation, pattern matching, and security best practices.
"""
import re
import hashlib
import hmac
import secrets
import base64
import json
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse, parse_qs
import ipaddress
from datetime import datetime, timedelta


class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VulnerabilityType(Enum):
    XSS = "cross_site_scripting"
    SQL_INJECTION = "sql_injection"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    CSRF = "cross_site_request_forgery"
    WEAK_CRYPTO = "weak_cryptography"
    INFO_DISCLOSURE = "information_disclosure"
    INPUT_VALIDATION = "input_validation"
    AUTHENTICATION = "authentication_bypass"
    AUTHORIZATION = "authorization_failure"


@dataclass
class SecurityFinding:
    vulnerability_type: VulnerabilityType
    threat_level: ThreatLevel
    description: str
    location: str
    evidence: str
    recommendation: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    false_positive_likelihood: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InputValidationResult:
    is_valid: bool
    sanitized_input: str
    violations: List[str] = field(default_factory=list)
    risk_level: ThreatLevel = ThreatLevel.LOW
    applied_filters: List[str] = field(default_factory=list)


class SecurityAnalyzer:
    """
    Comprehensive security analyzer for defensive security testing.
    Implements various security validation and analysis techniques.
    """
    
    # Common attack patterns for detection
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
        r'<svg[^>]*>.*?</svg>',
    ]
    
    SQL_INJECTION_PATTERNS = [
        r"(union\s+select|select\s+.*\s+from|\bor\s+1\s*=\s*1|\band\s+1\s*=\s*1)",
        r"(\binsert\s+into|\bupdate\s+\w+\s+set|\bdelete\s+from)",
        r"(drop\s+table|alter\s+table|create\s+table)",
        r"(exec\s*\(|execute\s*\(|sp_executesql)",
        r"(concat\s*\(|char\s*\(|ascii\s*\()",
        r"(sleep\s*\(|waitfor\s+delay|benchmark\s*\()",
        r"(load_file\s*\(|into\s+outfile|into\s+dumpfile)",
        r"(information_schema|mysql\.user|pg_user)",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\./',
        r'\.\.\\',
        r'%2e%2e%2f',
        r'%2e%2e%5c',
        r'%252e%252e%252f',
        r'\.\.%2f',
        r'\.\.%5c',
        r'/etc/passwd',
        r'/windows/system32',
        r'%00',
        r'%2500',
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$]',
        r'\$\([^)]*\)',
        r'`[^`]*`',
        r'\|\s*(cat|ls|ps|id|whoami|uname)',
        r'(nc|netcat|curl|wget)\s+',
        r'(rm|del|format)\s+',
        r'(chmod|chown)\s+',
        r'>\s*/dev/',
    ]
    
    def __init__(self, strict_mode: bool = True, custom_patterns: Optional[Dict[str, List[str]]] = None):
        """
        Initialize security analyzer.
        
        Args:
            strict_mode: Enable strict validation rules
            custom_patterns: Additional custom attack patterns
        """
        self.strict_mode = strict_mode
        self.custom_patterns = custom_patterns or {}
        self.findings: List[SecurityFinding] = []
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {
            VulnerabilityType.XSS: [re.compile(p, re.IGNORECASE | re.DOTALL) 
                                   for p in self.XSS_PATTERNS],
            VulnerabilityType.SQL_INJECTION: [re.compile(p, re.IGNORECASE | re.DOTALL) 
                                             for p in self.SQL_INJECTION_PATTERNS],
            VulnerabilityType.PATH_TRAVERSAL: [re.compile(p, re.IGNORECASE) 
                                              for p in self.PATH_TRAVERSAL_PATTERNS],
            VulnerabilityType.COMMAND_INJECTION: [re.compile(p, re.IGNORECASE) 
                                                 for p in self.COMMAND_INJECTION_PATTERNS],
        }
        
        # Add custom patterns
        for vuln_type, patterns in self.custom_patterns.items():
            try:
                vuln_enum = VulnerabilityType(vuln_type)
                if vuln_enum not in self.compiled_patterns:
                    self.compiled_patterns[vuln_enum] = []
                self.compiled_patterns[vuln_enum].extend([
                    re.compile(p, re.IGNORECASE | re.DOTALL) for p in patterns
                ])
            except (ValueError, re.error):
                pass  # Skip invalid patterns
    
    def validate_input(self, user_input: str, input_type: str = "general", 
                      max_length: int = 1000, allowed_chars: Optional[str] = None) -> InputValidationResult:
        """
        Comprehensive input validation with sanitization.
        
        Args:
            user_input: Input string to validate
            input_type: Type of input (email, url, filename, etc.)
            max_length: Maximum allowed length
            allowed_chars: Regex pattern for allowed characters
        
        Returns:
            InputValidationResult with validation details
        """
        if not isinstance(user_input, str):
            return InputValidationResult(
                is_valid=False,
                sanitized_input="",
                violations=["Input must be a string"],
                risk_level=ThreatLevel.HIGH
            )
        
        violations = []
        sanitized = user_input
        applied_filters = []
        risk_level = ThreatLevel.LOW
        
        # Length validation
        if len(user_input) > max_length:
            violations.append(f"Input exceeds maximum length of {max_length}")
            sanitized = sanitized[:max_length]
            applied_filters.append("length_truncation")
            risk_level = max(risk_level, ThreatLevel.MEDIUM)
        
        # Null byte detection
        if '\x00' in user_input:
            violations.append("Null bytes detected")
            sanitized = sanitized.replace('\x00', '')
            applied_filters.append("null_byte_removal")
            risk_level = max(risk_level, ThreatLevel.HIGH)
        
        # Control character detection
        control_chars = sum(1 for c in user_input if ord(c) < 32 and c not in '\t\n\r')
        if control_chars > 0:
            violations.append(f"Control characters detected: {control_chars}")
            sanitized = ''.join(c for c in sanitized if ord(c) >= 32 or c in '\t\n\r')
            applied_filters.append("control_char_removal")
            risk_level = max(risk_level, ThreatLevel.MEDIUM)
        
        # Type-specific validation
        if input_type == "email":
            email_result = self._validate_email(sanitized)
            violations.extend(email_result.violations)
            sanitized = email_result.sanitized_input
            applied_filters.extend(email_result.applied_filters)
            risk_level = max(risk_level, email_result.risk_level)
        
        elif input_type == "url":
            url_result = self._validate_url(sanitized)
            violations.extend(url_result.violations)
            sanitized = url_result.sanitized_input
            applied_filters.extend(url_result.applied_filters)
            risk_level = max(risk_level, url_result.risk_level)
        
        elif input_type == "filename":
            filename_result = self._validate_filename(sanitized)
            violations.extend(filename_result.violations)
            sanitized = filename_result.sanitized_input
            applied_filters.extend(filename_result.applied_filters)
            risk_level = max(risk_level, filename_result.risk_level)
        
        # Character allowlist validation
        if allowed_chars:
            try:
                pattern = re.compile(f'^[{re.escape(allowed_chars)}]*$')
                if not pattern.match(sanitized):
                    violations.append("Contains disallowed characters")
                    # Remove disallowed chars
                    allowed_pattern = re.compile(f'[{re.escape(allowed_chars)}]')
                    sanitized = ''.join(allowed_pattern.findall(sanitized))
                    applied_filters.append("character_filtering")
                    risk_level = max(risk_level, ThreatLevel.MEDIUM)
            except re.error:
                violations.append("Invalid allowed characters pattern")
        
        # Attack pattern detection
        attack_detected = self._detect_attack_patterns(user_input)
        if attack_detected:
            violations.extend([f"{vuln.value} pattern detected" for vuln in attack_detected])
            risk_level = ThreatLevel.CRITICAL
        
        is_valid = len(violations) == 0 or (not self.strict_mode and risk_level != ThreatLevel.CRITICAL)
        
        return InputValidationResult(
            is_valid=is_valid,
            sanitized_input=sanitized,
            violations=violations,
            risk_level=risk_level,
            applied_filters=applied_filters
        )
    
    def _validate_email(self, email: str) -> InputValidationResult:
        """Validate email address format."""
        violations = []
        sanitized = email.strip().lower()
        applied_filters = ["normalization"]
        risk_level = ThreatLevel.LOW
        
        # Basic email regex (simplified for demonstration)
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        if not email_pattern.match(sanitized):
            violations.append("Invalid email format")
            risk_level = ThreatLevel.MEDIUM
        
        # Check for suspicious patterns in email
        suspicious_patterns = ['javascript:', 'data:', 'vbscript:', '<script', 'onload=']
        for pattern in suspicious_patterns:
            if pattern in sanitized:
                violations.append(f"Suspicious pattern in email: {pattern}")
                risk_level = ThreatLevel.HIGH
        
        # Length checks
        local_part, _, domain = sanitized.rpartition('@')
        if len(local_part) > 64:
            violations.append("Email local part too long")
            risk_level = ThreatLevel.MEDIUM
        
        if len(domain) > 253:
            violations.append("Email domain too long")
            risk_level = ThreatLevel.MEDIUM
        
        return InputValidationResult(
            is_valid=len(violations) == 0,
            sanitized_input=sanitized,
            violations=violations,
            risk_level=risk_level,
            applied_filters=applied_filters
        )
    
    def _validate_url(self, url: str) -> InputValidationResult:
        """Validate URL format and security."""
        violations = []
        sanitized = url.strip()
        applied_filters = ["normalization"]
        risk_level = ThreatLevel.LOW
        
        try:
            parsed = urlparse(sanitized)
            
            # Scheme validation
            allowed_schemes = ['http', 'https', 'ftp', 'ftps']
            if parsed.scheme.lower() not in allowed_schemes:
                violations.append(f"Disallowed URL scheme: {parsed.scheme}")
                risk_level = ThreatLevel.HIGH
            
            # Check for dangerous schemes
            dangerous_schemes = ['javascript', 'data', 'vbscript', 'file']
            if parsed.scheme.lower() in dangerous_schemes:
                violations.append(f"Dangerous URL scheme: {parsed.scheme}")
                risk_level = ThreatLevel.CRITICAL
            
            # Hostname validation
            if parsed.hostname:
                # Check for IP addresses
                try:
                    ip = ipaddress.ip_address(parsed.hostname)
                    if ip.is_private or ip.is_loopback:
                        violations.append("URL points to private/loopback IP")
                        risk_level = ThreatLevel.HIGH
                except ValueError:
                    pass  # Not an IP address, continue with hostname validation
                
                # Check for suspicious hostnames
                suspicious_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
                if parsed.hostname.lower() in suspicious_hosts:
                    violations.append("URL points to localhost")
                    risk_level = ThreatLevel.HIGH
            
            # Path traversal check
            if '../' in parsed.path or '..\\' in parsed.path:
                violations.append("Path traversal detected in URL")
                risk_level = ThreatLevel.HIGH
            
            # Query parameter validation
            if parsed.query:
                params = parse_qs(parsed.query)
                for param_name, param_values in params.items():
                    for value in param_values:
                        attack_types = self._detect_attack_patterns(value)
                        if attack_types:
                            violations.append(f"Attack pattern in URL parameter {param_name}")
                            risk_level = ThreatLevel.CRITICAL
        
        except Exception as e:
            violations.append(f"URL parsing error: {str(e)}")
            risk_level = ThreatLevel.HIGH
        
        return InputValidationResult(
            is_valid=len(violations) == 0,
            sanitized_input=sanitized,
            violations=violations,
            risk_level=risk_level,
            applied_filters=applied_filters
        )
    
    def _validate_filename(self, filename: str) -> InputValidationResult:
        """Validate filename for security issues."""
        violations = []
        sanitized = filename.strip()
        applied_filters = ["normalization"]
        risk_level = ThreatLevel.LOW
        
        # Check for path traversal
        if '../' in filename or '..\\' in filename:
            violations.append("Path traversal in filename")
            sanitized = sanitized.replace('../', '').replace('..\\', '')
            applied_filters.append("path_traversal_removal")
            risk_level = ThreatLevel.HIGH
        
        # Check for absolute paths
        if filename.startswith('/') or (len(filename) > 1 and filename[1] == ':'):
            violations.append("Absolute path in filename")
            sanitized = sanitized.lstrip('/').lstrip('C:\\').lstrip('c:\\')
            applied_filters.append("absolute_path_removal")
            risk_level = ThreatLevel.MEDIUM
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
        for char in dangerous_chars:
            if char in filename:
                violations.append(f"Dangerous character in filename: {char}")
                sanitized = sanitized.replace(char, '_')
                applied_filters.append("dangerous_char_replacement")
                risk_level = max(risk_level, ThreatLevel.MEDIUM)
        
        # Check for reserved names (Windows)
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                         'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3',
                         'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
        
        name_without_ext = sanitized.split('.')[0].upper()
        if name_without_ext in reserved_names:
            violations.append(f"Reserved filename: {name_without_ext}")
            sanitized = f"safe_{sanitized}"
            applied_filters.append("reserved_name_prefix")
            risk_level = max(risk_level, ThreatLevel.MEDIUM)
        
        # Length validation
        if len(sanitized) > 255:
            violations.append("Filename too long")
            sanitized = sanitized[:255]
            applied_filters.append("length_truncation")
            risk_level = max(risk_level, ThreatLevel.MEDIUM)
        
        return InputValidationResult(
            is_valid=len(violations) == 0,
            sanitized_input=sanitized,
            violations=violations,
            risk_level=risk_level,
            applied_filters=applied_filters
        )
    
    def _detect_attack_patterns(self, input_str: str) -> List[VulnerabilityType]:
        """Detect known attack patterns in input."""
        detected_attacks = []
        
        for vuln_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(input_str):
                    detected_attacks.append(vuln_type)
                    break  # Found one pattern for this type, move to next type
        
        return detected_attacks
    
    def analyze_code_for_vulnerabilities(self, code: str, language: str = "python") -> List[SecurityFinding]:
        """
        Analyze code for common security vulnerabilities.
        
        Args:
            code: Source code to analyze
            language: Programming language (python, javascript, etc.)
        
        Returns:
            List of security findings
        """
        findings = []
        
        if language.lower() == "python":
            findings.extend(self._analyze_python_code(code))
        elif language.lower() in ["javascript", "js"]:
            findings.extend(self._analyze_javascript_code(code))
        else:
            # Generic analysis
            findings.extend(self._analyze_generic_code(code))
        
        return findings
    
    def _analyze_python_code(self, code: str) -> List[SecurityFinding]:
        """Analyze Python code for security issues."""
        findings = []
        lines = code.split('\n')
        
        # Check for dangerous functions
        dangerous_functions = {
            'eval(': (ThreatLevel.CRITICAL, "Use of eval() can lead to code injection", "CWE-95"),
            'exec(': (ThreatLevel.CRITICAL, "Use of exec() can lead to code injection", "CWE-95"),
            'os.system(': (ThreatLevel.HIGH, "Use of os.system() can lead to command injection", "CWE-78"),
            'subprocess.call(': (ThreatLevel.MEDIUM, "Subprocess usage should be reviewed for command injection", "CWE-78"),
            'pickle.loads(': (ThreatLevel.HIGH, "Pickle deserialization can lead to code execution", "CWE-502"),
            'yaml.load(': (ThreatLevel.HIGH, "YAML load without safe_load can lead to code execution", "CWE-502"),
            'shell=True': (ThreatLevel.MEDIUM, "Shell=True in subprocess can be dangerous", "CWE-78"),
        }
        
        for line_num, line in enumerate(lines, 1):
            for pattern, (level, desc, cwe) in dangerous_functions.items():
                if pattern in line:
                    findings.append(SecurityFinding(
                        vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                        threat_level=level,
                        description=desc,
                        location=f"Line {line_num}",
                        evidence=line.strip(),
                        recommendation=f"Replace {pattern} with safer alternatives",
                        cwe_id=cwe
                    ))
        
        # Check for hardcoded credentials
        credential_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token detected"),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, desc in credential_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        vulnerability_type=VulnerabilityType.INFO_DISCLOSURE,
                        threat_level=ThreatLevel.HIGH,
                        description=desc,
                        location=f"Line {line_num}",
                        evidence=line.strip(),
                        recommendation="Use environment variables or secure key management",
                        cwe_id="CWE-798"
                    ))
        
        return findings
    
    def _analyze_javascript_code(self, code: str) -> List[SecurityFinding]:
        """Analyze JavaScript code for security issues."""
        findings = []
        lines = code.split('\n')
        
        # Check for dangerous functions
        dangerous_patterns = {
            'eval(': (ThreatLevel.CRITICAL, "Use of eval() can lead to code injection"),
            'innerHTML': (ThreatLevel.MEDIUM, "innerHTML usage can lead to XSS if not sanitized"),
            'document.write(': (ThreatLevel.MEDIUM, "document.write() can introduce XSS vulnerabilities"),
            'window.location': (ThreatLevel.MEDIUM, "Direct location manipulation can be dangerous"),
            'setTimeout(': (ThreatLevel.LOW, "setTimeout with string parameter can be dangerous"),
            'setInterval(': (ThreatLevel.LOW, "setInterval with string parameter can be dangerous"),
        }
        
        for line_num, line in enumerate(lines, 1):
            for pattern, (level, desc) in dangerous_patterns.items():
                if pattern in line:
                    findings.append(SecurityFinding(
                        vulnerability_type=VulnerabilityType.XSS,
                        threat_level=level,
                        description=desc,
                        location=f"Line {line_num}",
                        evidence=line.strip(),
                        recommendation=f"Review usage of {pattern} for security implications"
                    ))
        
        return findings
    
    def _analyze_generic_code(self, code: str) -> List[SecurityFinding]:
        """Generic code analysis for common patterns."""
        findings = []
        
        # Check for potential SQL injection patterns
        sql_patterns = [
            r'SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*\+',
            r'INSERT\s+INTO\s+.*\s+VALUES\s*\(.*\+',
            r'UPDATE\s+.*\s+SET\s+.*\+',
            r'DELETE\s+FROM\s+.*\s+WHERE\s+.*\+',
        ]
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                findings.append(SecurityFinding(
                    vulnerability_type=VulnerabilityType.SQL_INJECTION,
                    threat_level=ThreatLevel.HIGH,
                    description="Potential SQL injection vulnerability",
                    location=f"Position {match.start()}-{match.end()}",
                    evidence=match.group(),
                    recommendation="Use parameterized queries instead of string concatenation",
                    cwe_id="CWE-89"
                ))
        
        return findings
    
    def generate_secure_token(self, length: int = 32, include_timestamp: bool = False) -> Dict[str, str]:
        """
        Generate cryptographically secure tokens.
        
        Args:
            length: Token length in bytes
            include_timestamp: Whether to include timestamp in token
        
        Returns:
            Dictionary with token information
        
        Raises:
            ValueError: For invalid length
        """
        if length < 16:
            raise ValueError("Token length must be at least 16 bytes")
        
        if length > 1024:
            raise ValueError("Token length cannot exceed 1024 bytes")
        
        # Generate random bytes
        random_bytes = secrets.token_bytes(length)
        
        # Create different token formats
        token_hex = secrets.token_hex(length)
        token_urlsafe = secrets.token_urlsafe(length)
        
        result = {
            'token_hex': token_hex,
            'token_urlsafe': token_urlsafe,
            'token_bytes_b64': base64.b64encode(random_bytes).decode('ascii'),
            'length_bytes': length,
            'entropy_bits': length * 8,
        }
        
        if include_timestamp:
            timestamp = datetime.now().isoformat()
            # Create a timestamped token (for demonstration only - not for production)
            timestamped_data = {
                'token': token_hex,
                'created_at': timestamp,
                'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
            }
            result['timestamped_token'] = base64.b64encode(
                json.dumps(timestamped_data).encode()
            ).decode('ascii')
        
        return result
    
    def verify_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Analyze password strength with detailed feedback.
        
        Args:
            password: Password to analyze
        
        Returns:
            Dictionary with strength analysis
        """
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        
        analysis = {
            'length': len(password),
            'strength_score': 0,
            'strength_level': 'very_weak',
            'requirements_met': [],
            'requirements_failed': [],
            'character_analysis': {},
            'common_patterns': [],
            'recommendations': []
        }
        
        # Character analysis
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        has_space = ' ' in password
        
        analysis['character_analysis'] = {
            'lowercase': has_lower,
            'uppercase': has_upper,
            'digits': has_digit,
            'special_chars': has_special,
            'spaces': has_space,
            'unique_chars': len(set(password))
        }
        
        # Length scoring
        if len(password) >= 8:
            analysis['requirements_met'].append('minimum_length')
            analysis['strength_score'] += 1
        else:
            analysis['requirements_failed'].append('minimum_length')
            analysis['recommendations'].append('Use at least 8 characters')
        
        if len(password) >= 12:
            analysis['strength_score'] += 1
        
        # Character variety scoring
        if has_lower:
            analysis['requirements_met'].append('lowercase')
            analysis['strength_score'] += 1
        else:
            analysis['requirements_failed'].append('lowercase')
            analysis['recommendations'].append('Include lowercase letters')
        
        if has_upper:
            analysis['requirements_met'].append('uppercase')
            analysis['strength_score'] += 1
        else:
            analysis['requirements_failed'].append('uppercase')
            analysis['recommendations'].append('Include uppercase letters')
        
        if has_digit:
            analysis['requirements_met'].append('digits')
            analysis['strength_score'] += 1
        else:
            analysis['requirements_failed'].append('digits')
            analysis['recommendations'].append('Include numbers')
        
        if has_special:
            analysis['requirements_met'].append('special_characters')
            analysis['strength_score'] += 1
        else:
            analysis['requirements_failed'].append('special_characters')
            analysis['recommendations'].append('Include special characters')
        
        # Pattern detection
        common_patterns = [
            (r'123', 'sequential_numbers'),
            (r'abc', 'sequential_letters'),
            (r'(.)\1{2,}', 'repeated_characters'),
            (r'password', 'contains_password'),
            (r'admin', 'contains_admin'),
            (r'user', 'contains_user'),
            (r'test', 'contains_test'),
            (r'qwerty', 'keyboard_pattern'),
            (r'asdf', 'keyboard_pattern'),
        ]
        
        for pattern, pattern_name in common_patterns:
            if re.search(pattern, password, re.IGNORECASE):
                analysis['common_patterns'].append(pattern_name)
                analysis['strength_score'] -= 1
                analysis['recommendations'].append(f'Avoid {pattern_name.replace("_", " ")}')
        
        # Entropy calculation (simplified)
        char_space = 0
        if has_lower:
            char_space += 26
        if has_upper:
            char_space += 26
        if has_digit:
            char_space += 10
        if has_special:
            char_space += 32
        
        if char_space > 0:
            import math
            entropy = len(password) * math.log2(char_space)
            analysis['entropy_bits'] = round(entropy, 2)
        else:
            analysis['entropy_bits'] = 0
        
        # Final strength level
        if analysis['strength_score'] >= 6:
            analysis['strength_level'] = 'very_strong'
        elif analysis['strength_score'] >= 5:
            analysis['strength_level'] = 'strong'
        elif analysis['strength_score'] >= 3:
            analysis['strength_level'] = 'medium'
        elif analysis['strength_score'] >= 1:
            analysis['strength_level'] = 'weak'
        else:
            analysis['strength_level'] = 'very_weak'
        
        return analysis
    
    def create_security_hash(self, data: str, algorithm: str = "sha256", 
                           salt: Optional[str] = None) -> Dict[str, str]:
        """
        Create secure hash with optional salt.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, sha512, blake2b)
            salt: Optional salt value
        
        Returns:
            Dictionary with hash information
        
        Raises:
            ValueError: For unsupported algorithms
        """
        if not isinstance(data, str):
            raise TypeError("Data must be a string")
        
        supported_algorithms = ['sha256', 'sha512', 'blake2b', 'blake2s']
        if algorithm not in supported_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}. "
                           f"Supported: {supported_algorithms}")
        
        # Generate salt if not provided
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine data and salt
        salted_data = data + salt
        
        # Create hash
        if algorithm == 'sha256':
            hash_obj = hashlib.sha256(salted_data.encode('utf-8'))
        elif algorithm == 'sha512':
            hash_obj = hashlib.sha512(salted_data.encode('utf-8'))
        elif algorithm == 'blake2b':
            hash_obj = hashlib.blake2b(salted_data.encode('utf-8'))
        elif algorithm == 'blake2s':
            hash_obj = hashlib.blake2s(salted_data.encode('utf-8'))
        
        hash_value = hash_obj.hexdigest()
        
        return {
            'algorithm': algorithm,
            'hash': hash_value,
            'salt': salt,
            'salted_hash': f"{algorithm}${salt}${hash_value}",
            'hash_length': len(hash_value),
            'salt_length': len(salt)
        }
    
    def verify_hash(self, data: str, salted_hash: str) -> bool:
        """
        Verify data against a salted hash.
        
        Args:
            data: Original data
            salted_hash: Hash in format "algorithm$salt$hash"
        
        Returns:
            True if hash matches, False otherwise
        
        Raises:
            ValueError: For invalid hash format
        """
        try:
            parts = salted_hash.split('$')
            if len(parts) != 3:
                raise ValueError("Invalid hash format")
            
            algorithm, salt, expected_hash = parts
            
            # Recreate hash
            new_hash_info = self.create_security_hash(data, algorithm, salt)
            
            # Constant-time comparison
            return hmac.compare_digest(new_hash_info['hash'], expected_hash)
            
        except Exception as e:
            raise ValueError(f"Hash verification failed: {str(e)}")
    
    def get_findings_summary(self) -> Dict[str, Any]:
        """Get summary of all security findings."""
        if not self.findings:
            return {
                'total_findings': 0,
                'by_severity': {},
                'by_type': {},
                'high_priority_count': 0
            }
        
        severity_counts = {}
        type_counts = {}
        high_priority = 0
        
        for finding in self.findings:
            # Count by severity
            severity = finding.threat_level.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by type
            vuln_type = finding.vulnerability_type.value
            type_counts[vuln_type] = type_counts.get(vuln_type, 0) + 1
            
            # Count high priority (high/critical)
            if finding.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                high_priority += 1
        
        return {
            'total_findings': len(self.findings),
            'by_severity': severity_counts,
            'by_type': type_counts,
            'high_priority_count': high_priority,
            'findings': self.findings
        }