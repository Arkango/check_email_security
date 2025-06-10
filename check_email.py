import dns.resolver
import csv
import argparse
import dns.exception

# Define the public DNS resolvers
dns_resolvers = [
    '8.8.8.8',    # Google DNS
    '1.1.1.1',    # Cloudflare DNS
    '9.9.9.9'     # Quad9 DNS
]

# Function to query DNS records using multiple resolvers
def query_dns(domain, record_type):
    for resolver_ip in dns_resolvers:
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [resolver_ip]
            answers = resolver.resolve(domain, record_type)
            return [str(rdata) for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            continue
    return None

# Function to check SPF, DKIM, and DMARC records for a domain
def check_email_security(domain):
    spf_record = query_dns(domain, 'TXT')
    print(f"SPF Record for {domain}: {spf_record}")
    dmarc_record = query_dns('_dmarc.' + domain, 'TXT')
    print(f"DMARC Record for {domain}: {dmarc_record}")
    dkim_record = query_dns('default._domainkey.' + domain, 'TXT')
    print(f"DKIM Record for {domain}: {dkim_record}")

    spf_value = next((record for record in spf_record if record.startswith('"v=spf1')), 'No SPF record') if spf_record else 'No SPF record'
    dmarc_value = next((record for record in dmarc_record if record.startswith('"v=DMARC1')), 'No DMARC record') if dmarc_record else 'No DMARC record'
    dkim_value = next((record for record in dkim_record if record.startswith('"v=DKIM1')), 'No DKIM record') if dkim_record else 'No DKIM record'

    interpretation = 'Not secure: No authentication mechanisms in place'
    if spf_value != 'No SPF record' or dkim_value != 'No DKIM record':
        if dmarc_value != 'No DMARC record':
            if 'p=reject' in dmarc_value or 'p=quarantine' in dmarc_value:
                interpretation = 'Best practice: Strong protection against spoofing and phishing'
            else:
                interpretation = 'Not secure: DMARC policy is monitoring only'
        else:
            interpretation = 'Not secure: Missing DMARC record'
    return [domain, spf_value, dmarc_value, dkim_value, interpretation]

# Function to check email security for multiple domains from a file
def check_multiple_domains(file_path):
    results = []
    with open(file_path, 'r') as file:
        domains = file.readlines()
        for domain in domains:
            domain = domain.strip()
            results.append(check_email_security(domain))
    return results

# Function to save results to a CSV file
def save_to_csv(results, output_file):
    headers = ['Domain', 'SPF Record', 'DMARC Record', 'DKIM Record', 'Interpretation']
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(results)
def main():
    parser = argparse.ArgumentParser(description="Check email security records for a domain or list of domains.")
    parser.add_argument('-d', '--domain', type=str, help="Single domain to check")
    parser.add_argument('-f', '--file', type=str, help="File containing list of domains to check")
    args = parser.parse_args()

    results = []
    if args.domain:
        results.append(check_email_security(args.domain))
    elif args.file:
        with open(args.file, 'r') as f:
            domains = f.read().splitlines()
            for domain in domains:
                results.append(check_email_security(domain))
    else:
        print("Please provide a domain or a file containing domains.")
        return

    with open('email_security_check.csv', 'w', newline='') as csvfile:
        fieldnames = ['Domain', 'SPF Record', 'DMARC Record', 'DKIM Record', 'Interpretation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({
                'Domain': result[0],
                'SPF Record': result[1],
                'DMARC Record': result[2],
                'DKIM Record': result[3],
                'Interpretation': result[4]
            })

    print("Results saved to email_security_check.csv")

if __name__ == "__main__":
    main()