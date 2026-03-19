# Email Deliverability Best Practices Guide

## 📋 Table of Contents

1. [Legal Compliance](#legal-compliance)
2. [Domain Authentication](#domain-authentication)
3. [List Hygiene](#list-hygiene)
4. [Content Best Practices](#content-best-practices)
5. [Sending Infrastructure](#sending-infrastructure)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## ⚖️ Legal Compliance

### CAN-SPAM Act (USA)

**Requirements:**
- ✅ Include valid physical mailing address
- ✅ Provide clear unsubscribe mechanism
- ✅ Honor unsubscribe requests within 10 days
- ✅ Accurate subject lines (no deception)
- ✅ Identify message as advertisement (if applicable)

**Penalties:** Up to $50,000 per violation

### GDPR (Europe)

**Requirements:**
- ✅ Explicit opt-in consent (no pre-checked boxes)
- ✅ Clear purpose for data collection
- ✅ Easy withdrawal of consent
- ✅ Data processing records
- ✅ Privacy policy link

**Penalties:** Up to €20M or 4% of global revenue

### CASL (Canada)

**Requirements:**
- ✅ Express or implied consent
- ✅ Identification information
- ✅ Unsubscribe mechanism

**Penalties:** Up to CAD $10M

### ✅ Implementation in This Codebase

```bash
# Double opt-in system
python opt_in_manager.py subscribe user@example.com

# Generate compliant footers
python compliance_footer.py

# Export consent records (GDPR)
python opt_in_manager.py export consent_records.json
```

---

## 🔐 Domain Authentication

### SPF (Sender Policy Framework)

**What it does:** Specifies which servers can send email for your domain

**Setup:**
```dns
; TXT record for your domain
@ IN TXT "v=spf1 include:_spf.google.com ~all"
```

**Best Practices:**
- Use `~all` (softfail) initially, upgrade to `-all` (fail) after testing
- Keep under 255 characters
- Maximum 10 DNS lookups (includes)

**Check with:**
```bash
python domain_auth_checker.py yourdomain.com
```

### DKIM (DomainKeys Identified Mail)

**What it does:** Adds cryptographic signature to verify email authenticity

**Setup (Gmail/Google Workspace):**
1. Go to Google Admin Console
2. Navigate to Apps > Google Workspace > Gmail
3. Click "Authenticate email address"
4. Generate DKIM key
5. Add DNS TXT record:
```dns
google._domainkey IN TXT "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A..."
```
6. Enable DKIM in admin console

### DMARC (Domain-based Message Authentication)

**What it does:** Tells receivers what to do if SPF/DKIM fails

**Setup:**
```dns
; TXT record at _dmarc.yourdomain.com
_dmarc IN TXT "v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomain.com; pct=100"
```

**Policy Progression:**
1. Start with `p=none` (monitor only)
2. After 2-4 weeks, move to `p=quarantine`
3. Finally, `p=reject` (maximum protection)

**Tags Explained:**
- `p=none|quarantine|reject` - Policy for failed emails
- `rua=mailto:...` - Email for aggregate reports
- `ruf=mailto:...` - Email for forensic reports
- `pct=100` - Percentage of emails to apply policy

---

## 🧹 List Hygiene

### Double Opt-In

**Why:** Ensures subscribers actually want your emails

**Implementation:**
```bash
# Add subscriber (sends confirmation email)
python opt_in_manager.py subscribe user@example.com

# User clicks confirmation link
# Subscription confirmed automatically
```

### Regular Cleaning

**Remove these subscribers:**
- Hard bounces (immediate removal)
- Inactive 90+ days (re-engagement campaign first)
- Spam complainers (immediate removal)
- Invalid emails (syntax errors, dead domains)

**Tools:**
```bash
# Find inactive subscribers
python engagement_tracker.py inactive 90

# Clean invalid emails
python email_list_manager.py clean

# View bounce statistics
python bounce_handler.py stats
```

### Segmentation Strategy

**By Engagement:**
- **Highly Engaged** (score 80-100): Send all campaigns
- **Engaged** (score 60-79): Regular sending
- **Moderately Engaged** (40-59): Reduce frequency
- **Low Engagement** (20-39): Re-engagement campaign
- **Inactive** (0-19): Sunset or remove

```bash
# Get segments
python engagement_tracker.py segment
```

---

## 📝 Content Best Practices

### Avoid Spam Trigger Words

**High Risk (Avoid):**
- "Free money", "Cash bonus", "Risk free"
- "Make money fast", "Work from home"
- "Congratulations", "You have won"
- "Act now", "Urgent", "Immediate"
- "Click here", "Order now"

**Medium Risk (Use Carefully):**
- "Special offer", "Limited time"
- "Discount", "Sale", "Save big"
- "Best price", "Lowest price"

### Subject Line Best Practices

**Do:**
- Keep under 50 characters (mobile optimization)
- Personalize with name or company
- Create genuine urgency (real deadlines)
- Test with spam checker

**Don't:**
- Use ALL CAPS
- Use excessive punctuation (!!!, ???)
- Use misleading claims
- Use emoji excessively

### HTML Best Practices

**Image-to-Text Ratio:**
- Minimum 60% text, 40% images
- Always include alt text
- Don't send image-only emails

**Code Quality:**
- Use inline CSS (not external stylesheets)
- Keep HTML under 102KB (Gmail clipping)
- Test across email clients

### Spam Score Checking

```bash
# Check template before sending
python spam_checker.py your_template
```

---

## 🖥️ Sending Infrastructure

### IP Warm-up

**New IP/Domain Schedule:**

| Week | Daily Volume | Delay Between Emails |
|------|--------------|---------------------|
| 1 | 20-50 | 2-5 seconds |
| 2 | 50-100 | 2-5 seconds |
| 3 | 100-250 | 2-5 seconds |
| 4 | 250-500 | 1-3 seconds |
| 5+ | 500+ | 1-3 seconds |

**Implementation:**
```bash
# Start warm-up
python warmup_manager.py start your_email@gmail.com

# Check progress
python warmup_manager.py status <session_id>
```

### SMTP Rotation

**Why:** Distributes sending across multiple accounts

**Setup:**
```bash
# Add multiple SMTP accounts
python smtp_account_manager.py add "Account1" "email1@gmail.com" "password" "smtp.gmail.com" 587 500
python smtp_account_manager.py add "Account2" "email2@gmail.com" "password" "smtp.gmail.com" 587 500

# Get next account (round-robin)
python smtp_account_manager.py next
```

### Rate Limiting

**Recommended Limits by Provider:**

| Provider | Daily Limit | Hourly Limit | Delay |
|----------|-------------|--------------|-------|
| Gmail (free) | 500 | ~100 | 30-60s |
| Google Workspace | 2,000 | ~500 | 10-30s |
| Outlook.com | 300 | ~100 | 30-60s |
| SendGrid (free) | 100 | 100 | 1s |
| Amazon SES | 200+ | Varies | 1s |

**Configuration (.env):**
```env
BATCH_SIZE=25
DELAY_BETWEEN_BATCHES=30
DELAY_BETWEEN_EMAILS=1.0
DELAY_MIN=1.0
DELAY_MAX=3.0
```

---

## 📊 Monitoring & Maintenance

### Key Metrics to Track

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Open Rate | >20% | 10-20% | <10% |
| Click Rate | >2% | 1-2% | <1% |
| Bounce Rate | <2% | 2-5% | >5% |
| Unsubscribe Rate | <0.5% | 0.5-1% | >1% |
| Spam Complaints | <0.1% | 0.1-0.3% | >0.3% |

### Daily Checks

```bash
# View campaign statistics
python stats_dashboard.py

# Check bounce rate
python bounce_handler.py stats

# Review engagement
python engagement_tracker.py top 20
```

### Weekly Tasks

- [ ] Review spam complaint reports
- [ ] Clean hard bounces from list
- [ ] Check domain authentication status
- [ ] Monitor sender reputation

### Monthly Tasks

- [ ] Remove inactive subscribers (90+ days)
- [ ] A/B test subject lines and content
- [ ] Review and update email templates
- [ ] Analyze engagement trends

---

## 🔧 Troubleshooting

### Emails Going to Spam

**Checklist:**
1. ✅ Verify SPF/DKIM/DMARC setup
2. ✅ Check spam score of content
3. ✅ Review bounce rate (<2%)
4. ✅ Ensure double opt-in is enabled
5. ✅ Check IP/domain reputation
6. ✅ Reduce sending volume temporarily
7. ✅ Warm up domain if new

**Tools:**
```bash
# Check domain auth
python domain_auth_checker.py yourdomain.com

# Check spam score
python spam_checker.py your_template

# View engagement
python engagement_tracker.py segment
```

### High Bounce Rate

**Actions:**
1. Remove hard bounces immediately
2. Validate email list before sending
3. Use double opt-in for new subscribers
4. Clean list regularly

```bash
# Clean invalid emails
python email_list_manager.py clean

# View bounces
python bounce_handler.py list
```

### Low Open Rates

**Solutions:**
1. Improve subject lines
2. Segment by engagement
3. Send at optimal times
4. Clean inactive subscribers
5. A/B test different approaches

```bash
# Create A/B test
python ab_test_manager.py demo

# Get inactive subscribers
python engagement_tracker.py inactive 90
```

### Domain/IP Blacklisted

**Recovery Steps:**
1. Identify blacklist (use mxtoolbox.com)
2. Fix the underlying issue
3. Request delisting
4. Reduce sending volume
5. Focus on engaged subscribers only
6. Consider new IP/domain if severe

---

## 🛠️ Quick Reference Commands

```bash
# Pre-send checklist
python domain_auth_checker.py yourdomain.com  # Check authentication
python spam_checker.py your_template          # Check spam score
python email_list_manager.py clean            # Clean invalid emails

# Subscriber management
python opt_in_manager.py subscribe user@example.com  # Add subscriber
python opt_in_manager.py stats                       # View stats
python engagement_tracker.py segment                 # View segments

# Campaign management
python warmup_manager.py start email@gmail.com       # Warm up account
python smtp_account_manager.py list                  # List SMTP accounts
python bounce_handler.py stats                       # Check bounces

# Compliance
python compliance_footer.py                          # Generate footer
python opt_in_manager.py export consent.json         # Export consent
```

---

## 📚 Additional Resources

### Tools
- **MXToolbox** - Check blacklists, DNS records
- **Google Postmaster Tools** - Monitor Gmail deliverability
- **Mail-Tester.com** - Test email spam score
- **Litmus** - Email client testing
- **Email on Acid** - Email testing platform

### Documentation
- [Gmail Bulk Sender Guidelines](https://support.google.com/mail/answer/188131)
- [Yahoo Bulk Sender Guidelines](https://postmaster.yahooinc.com/best-practices)
- [Microsoft Smart Network Data](https://sendersupport.olc.protection.outlook.com/snds/)

### RFCs
- [RFC 7208 - SPF](https://tools.ietf.org/html/rfc7208)
- [RFC 6376 - DKIM](https://tools.ietf.org/html/rfc6376)
- [RFC 7489 - DMARC](https://tools.ietf.org/html/rfc7489)

---

## ⚠️ What NOT to Do

❌ **Never:**
- Buy email lists
- Scrape emails from websites
- Send to purchased leads without consent
- Hide unsubscribe link
- Use misleading subject lines
- Send from multiple domains to evade filters
- Ignore bounce/complaint rates
- Send to inactive subscribers repeatedly

✅ **Always:**
- Get explicit consent
- Make unsubscribing easy
- Be transparent about content
- Monitor engagement metrics
- Respect subscriber
- Keep authentication records
- Test before sending

---

**Remember:** Good deliverability is built on trust with both subscribers and email providers. Focus on sending valuable content to people who want to receive it.
