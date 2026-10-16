# Claim audit (human check of the LLM judge's labels)

For each claim: is it supported by the evidence? Mark `verdict: [y]` (supported) or
`verdict: [n]` (not supported). Then run `uv run python -m eval.calibration_eval --apply-audit`.

## claim-000  (agent text-092)

**Claim:** In developing its litigation liability reserves, Eli Lilly considers the nature and number of other similar current and past matters.

> [P1] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P2] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P3] We are subject to a substantial number of claims, litigation, and investigations involving various current and historical products and practices. These claims relate to how we commercialize and/or how we price our products, product safety, our operations as well as contractual matters and other disputes. We have also filed lawsuits and taken other legal actions to protect our intellectual property and address unlawful practices. See Item 8, "Financial Statements and Supplementary Data—Note 16: Contingencies," for more information on certain matters. Like many companies in our industry, from time to time investigations into aspects of our business include inquiries, subpoenas, and other types

> [P4] initiated enforcement or other actions across industries to seek alignment with policy initiatives. Because of the nature of pharmaceutical products and our evolving business, we are, and could increasingly become, subject to large numbers of product liability claims for our previous, current, or future products, or to further litigation or investigations, including related to product safety, marketing, pricing, or other commercial practices. Some of these matters involve or may involve numerous plaintiffs and parties seeking large or indeterminate financial claims and may remain unresolved for several years. Such matters could negatively impact our reputation, affect our results of operatio

> [P5] We derive a significant percentage of our total revenue from relatively few products and sell our products through consolidated supply chain entities, which subjects us to various risks. We derived direct product and/or collaboration and other revenues of more than $3 billion for each of Mounjaro, Zepbound, Verzenio, Trulicity, Taltz, and Jardiance (including Glyxambi, Synjardy, and Trijardy XR) that collectively accounted for 82 percent of our total revenues in 2025. In particular, Mounjaro and Zepbound accounted for 56 percent of our total revenues in 2025, and we expect cardiometabolic health products will continue to represent a significant and growing portion of our business, revenues,

> [P6] Risks Related to Litigation and Government Regulation •We are party to litigation and investigations related to our products, how we price or commercialize our products, and other aspects of our business, which could adversely affect our business, and we are self-insured for such matters.

judge: supported

verdict: [ ]

## claim-001  (agent cross-178)

**Claim:** Revenue increase was driven by increased volume, primarily from Mounjaro and Zepbound, though this was partially offset by lower realized prices for those same products.

> [P1] (Tables present dollars in millions, except per-share data, and numbers may not add due to rounding) General Management's discussion and analysis of results of operations and financial condition is intended to assist the reader in understanding and assessing significant changes and trends related to our results of operations and financial position. This discussion and analysis should be read in conjunction with Item 8, "Financial Statements and Supplementary Data." Certain statements in this Item 7 constitute forward-looking statements. Various risks and uncertainties, including those discussed in "Forward-Looking Statements" and Item 1A, "Risk Factors," may cause our actual results, financi

> [P2] 2,910 3,280 (11) Income taxes 5,091 2,090 144 Effective tax rate 19.8 % 16.5 % Gross margin as a percent of revenue in 2025 increased 1.7 percentage points compared with 2024, primarily driven by favorable product mix and improved cost of production, partially offset by lower realized prices. Research and development expenses increased 21 percent in 2025, primarily driven by continued investments in our early and late-stage portfolio. Marketing, selling, and administrative expenses increased 29 percent in 2025, primarily driven by promotional efforts supporting ongoing and planned launches.

> [P3] Percent change 43 % 48 % 45 % In the U.S., the volume increase and the lower realized prices in 2025 were primarily driven by Mounjaro and Zepbound. Outside the U.S., the volume increase in 2025 was primarily driven by Mounjaro. The following table summarizes our revenue, including net product revenue and collaboration and other revenue, by product in 2025 compared with 2024:

> [P4] In addition to our cash and cash equivalents, we held total investments of $2.9 billion and $3.4 billion as of December 31, 2025 and 2024, respectively. As of December 31, 2025, we had approximately $902 million of unfunded commitments to invest in venture capital funds, which we anticipate will be paid over a period of up to 10 years. See Note 7 to the consolidated financial statements for additional information. We paid $3.0 billion in 2025 for acquired IPR&D primarily related to the acquisitions of Scorpion's PI3Kα inhibitor program STX-478 and of SiteOne. We paid $3.3 billion in 2024 for acquired IPR&D primarily related to the acquisition of Morphic. See Note 4 to the consolidated financ

> [P5] As of December 31, 2025, a 5 percent change in the amount of uncertain tax positions and the valuation allowance would result in a change in net income of $160 million and $61 million, respectively. LEGAL AND REGULATORY MATTERS Information relating to certain legal proceedings can be found in Note 16 to the consolidated financial statements and is incorporated here by reference.

> [P6] Gross Margin, Costs, and Expenses The following table summarizes our gross margin, costs, and expenses: Year Ended December 31, Percent Change 2025 2024 Gross margin $ 54,127 $ 36,625 48 Gross margin as a percent of revenue 83.0 % 81.3 % Research and development $ 13,337 $ 10,991 21 Marketing, selling, and administrative 11,094 8,594 29 Acquired in-process research and development

> [F1] ticker = LLY, fiscal_year = 2025, metric = net_income, value = 20640000000.0

judge: supported

verdict: [ ]

## claim-002  (agent text-099)

**Claim:** UPS determines accruals for self‑insured workers' compensation, automobile, and general liabilities using actuarial estimates of the aggregate liability for claims incurred and an estimate of incurred but not reported claims, on an undiscounted basis

> [P1] Insurance and claims expense could materially adversely affect us. We have a combination of both self-insurance and high-deductible insurance programs for the risks arising out of our business and operations, including claims exposure resulting from cargo loss, cyber-attacks, personal injury, property damage, aircraft and related liabilities, business interruption and workers' compensation. Self-insured workers' compensation, automobile and general liabilities are determined using actuarial estimates of the aggregate liability for claims incurred and an estimate of incurred but not reported claims, on an undiscounted basis. Our accruals for insurance reserves reflect certain actuarial assump

> [P2] Insurance and claims expense could materially adversely affect us. We have a combination of both self-insurance and high-deductible insurance programs for the risks arising out of our business and operations, including claims exposure resulting from cargo loss, cyber-attacks, personal injury, property damage, aircraft and related liabilities, business interruption and workers' compensation. Self-insured workers' compensation, automobile and general liabilities are determined using actuarial estimates of the aggregate liability for claims incurred and an estimate of incurred but not reported claims, on an undiscounted basis. Our accruals for insurance reserves reflect certain actuarial assump

> [P3] Workers' compensation, automobile liability and general liability insurance claims may take a number of years to resolve. Consequently, actuarial estimates are required to project the ultimate cost that will be incurred to resolve a claim. Several factors can affect the actual cost, or severity, of a claim, including: •Risk retention limits; •Length of time a claim remains open; •Trends in healthcare and litigation costs; •Results of any related litigation; and •Changes in legislation. UNITED PARCEL SERVICE, INC. AND SUBSIDIARIES MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS Furthermore, claims may emerge in future years for events that occurred in a p

> [P4] Our finite-lived intangible assets are amortized over their estimated useful lives. These assets are tested for impairment as part of asset groups that may include other long-lived assets. See "Critical Accounting Estimates – Depreciation, Residual Value and Impairment of Property, Plant and Equipment" for a discussion of estimates impacting asset groups. In addition, a reduction in expected useful life, or a decision to sell or abandon an intangible asset before the end of its useful life, may increase amortization expense, which could have a material impact on our results of operations. UNITED PARCEL SERVICE, INC. AND SUBSIDIARIES MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION

> [P5] We are predominantly self-insured for a number of different risk categories, such as general liability (including product liability), property loss, workers’ compensation, employee group medical, employment practices liability and wage and hour claims, automobile claims, and cybersecurity and privacy liability, with insurance coverage for certain catastrophic risks above the self-insurance levels. The types and amounts of insurance may vary from time to time based on our decisions with respect to risk retention and regulatory requirements. The occurrence of significant claims, a substantial rise in costs to maintain our insurance, the failure to maintain adequate insurance coverage, or dispu

> [P6] Due to the complexity and inherent uncertainty associated with the estimation of our workers’ compensation, automobile and general claims liabilities, the third-party actuary develops a range of expected losses. We believe our estimated reserves for such claims are adequate; however, actual experience in claims frequency and/or severity of claims could materially differ from our estimates and affect our results of operations. We also sponsor several health and welfare insurance plans for our employees. Liabilities and expenses related to these plans are based on estimates of the number of employees and eligible dependents covered under the plans, global health events, anticipated utilization

judge: supported

verdict: [ ]

## claim-003  (agent text-092)

**Claim:** In developing its litigation liability reserves, Eli Lilly considers the merits and jurisdiction of the litigation.

> [P1] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P2] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P3] We are subject to a substantial number of claims, litigation, and investigations involving various current and historical products and practices. These claims relate to how we commercialize and/or how we price our products, product safety, our operations as well as contractual matters and other disputes. We have also filed lawsuits and taken other legal actions to protect our intellectual property and address unlawful practices. See Item 8, "Financial Statements and Supplementary Data—Note 16: Contingencies," for more information on certain matters. Like many companies in our industry, from time to time investigations into aspects of our business include inquiries, subpoenas, and other types

> [P4] initiated enforcement or other actions across industries to seek alignment with policy initiatives. Because of the nature of pharmaceutical products and our evolving business, we are, and could increasingly become, subject to large numbers of product liability claims for our previous, current, or future products, or to further litigation or investigations, including related to product safety, marketing, pricing, or other commercial practices. Some of these matters involve or may involve numerous plaintiffs and parties seeking large or indeterminate financial claims and may remain unresolved for several years. Such matters could negatively impact our reputation, affect our results of operatio

> [P5] We derive a significant percentage of our total revenue from relatively few products and sell our products through consolidated supply chain entities, which subjects us to various risks. We derived direct product and/or collaboration and other revenues of more than $3 billion for each of Mounjaro, Zepbound, Verzenio, Trulicity, Taltz, and Jardiance (including Glyxambi, Synjardy, and Trijardy XR) that collectively accounted for 82 percent of our total revenues in 2025. In particular, Mounjaro and Zepbound accounted for 56 percent of our total revenues in 2025, and we expect cardiometabolic health products will continue to represent a significant and growing portion of our business, revenues,

> [P6] Risks Related to Litigation and Government Regulation •We are party to litigation and investigations related to our products, how we price or commercialize our products, and other aspects of our business, which could adversely affect our business, and we are self-insured for such matters.

judge: supported

verdict: [ ]

## claim-004  (agent text-136)

**Claim:** Target Circle Card offerings provide a 5 percent discount on nearly all purchases, free standard and 2‑day shipping on eligible digital‑channel items, and extended returns

> [P1] We generate revenue through a variety of other sources, including Roundel, which provides advertising services to vendors and other third parties, including marketplace sellers; credit card profit sharing related to our Target Circle Card program; our third-party digital marketplace, Target Plus; membership fees; and others. Customer Loyalty Program We seek to drive customer loyalty and trip frequency through our Target Circle™ program, which provides benefits to guests that vary depending on their engagement with the program through one or more of the following offerings: •a free membership providing deals and bonuses including instant discounts and Target Circle Rewards offerings redeemabl

> [P2] (53 weeks) 2024 (52 weeks) 2025 (52 weeks) $107.4 $106.6 $104.8 (a) 2023 consisted of 53 weeks. The extra week in 2023 contributed $1.7 billion of Net Sales. TARGET CORPORATION 2025 Form 10-K 3 BUSINESS Table of Contents Index to Financial Statements Merchandise Sales by Fulfillment Channel Financial Highlights For information on key financial highlights, see Part II, Item 7, Management's Discussion and Analysis of Financial Condition and Results of Operations (MD&A).

> [P3] Strategy Target’s strategy is grounded in our purpose to help all families discover the joy of everyday life and our ambition to be the most delightful experience in retail. We differentiate through design, style, and value, and a curated multi-category assortment delivered across stores and digital channels. Our strategy is centered on four priorities. Lead with Merchandising Authority. Curating design-led, trend-right assortments that combine quality, newness, and value. We focus on categories and brands where we can offer a distinctive and relevant experience for our guests. Elevate the Guest Experience. Elevating the guest experience by making shopping easy, inspiring, and friendly. Our

> [P4] Our year-end cash and cash equivalents balance increased to $5.5 billion from $4.8 billion in 2024. Our cash and cash equivalents balance includes short-term investments of $4.6 billion and $3.9 billion as of January 31, 2026, and February 1, 2025, respectively. Our investment policy is designed to preserve principal and liquidity of our short-term investments. This policy allows investments in large money market funds or in highly rated direct short-term instruments that mature in 60 days or less. We also place dollar limits on our investments in individual funds or instruments. Operating Cash Flows Cash flows provided by operating activities were $6.6 billion in 2025 compared with $7.4 bil

> [P5] Distribution Most merchandise is distributed to our stores through our network of distribution centers. Common carriers ship merchandise to and from our distribution centers. Vendors or third-party distributors ship certain food and beverage items and other merchandise directly to our stores. Merchandise sold through our digital channels is distributed to our guests through guest pick-up at our stores, via common carriers (from stores, supply chain facilities, vendors, and third-party distributors), and same-day delivery. Our stores fulfill the majority of digitally originated sales, which allows improved product availability, faster fulfillment times, reduced shipping costs, and allows us t

> [P6] •Continued our longstanding commitment to community engagement and giving, including giving 5 percent of profit to communities, as well as over 1 million team member volunteer hours annually. Business Environment Beginning in 2025, the U.S. imposed a variety of additional tariffs on a wide range of imported products using various legal authorities, including IEEPA. Those additional tariffs were subsequently modified through incremental increases, decreases, pauses, and limited exemptions. Approximately one-half of the merchandise we offer is sourced from outside the U.S., either directly or through our vendors, with China as the single largest source of merchandise we import. On February 20,

judge: supported

verdict: [ ]

## claim-005  (baseline text-132)

**Claim:** Apple identifies price as a principal competitive factor important to its success

> [P1] The markets for the Company’s products and services are highly competitive and are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. The markets in which the Company competes are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements by competitors. Many of the Company’s competitors seek to compete primarily through aggressive pricing and very low cost structures, and by imitating the Company’s products and infringing on its intellec

> [P2] The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs and develops nearly the entire solution for its products, including the hardware, operating system, numerous software applications and related services. Principal competitive factors important to the Company include price, product and service features (including security features), relative price and performance, product and service quality and reliability, design innovation, a strong third-party software and accessories ecosystem, marketing and distribution capability, service and suppor

> [P3] The Company’s products and services are offered in highly competitive global markets. These markets are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. These markets are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements. The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs an

> [P4] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number of factors, including timely and successful development, market accepta

> [P5] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, navigate global regulatory requirements and barriers to market access, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number

judge: supported

verdict: [ ]

## claim-006  (baseline text-129)

**Claim:** It was 16% higher than in 2023.

> [P1] Goldman Sachs 2025 Form 10-K THE GOLDMAN SACHS GROUP, INC. AND SUBSIDIARIES Management’s Discussion and Analysis Net revenues in Equities were $13.43 billion, 16% higher than 2023, reflecting significantly higher net revenues in Equities intermediation, primarily driven by derivatives, and higher net revenues in Equities financing, driven by prime financing. Net revenues in Other were $561 million for 2024, compared with $80 million for 2023, with the increase primarily reflecting significantly lower net losses on hedges. Provision for credit losses was $84 million for 2024, compared with $430 million for 2023. Provisions for 2023 primarily reflected net provisions related to the commercial

> [P2] The increase in FICC intermediation net revenues reflected the impact of improved market-making conditions on our inventory, partially offset by lower client activity. The following provides information about our FICC intermediation net revenues by business, compared with results for 2023: •Net revenues in currencies, mortgages and credit products reflected the impact of improved market-making conditions on our inventory. •Net revenues in interest rate products and commodities primarily reflected lower client activity. Net revenues in Equities were $13.43 billion, 16% higher than 2023, reflecting significantly higher net revenues in Equities intermediation, primarily driven by derivatives, a

> [P3] The increase in Equity investments net revenues primarily reflected significantly higher net gains from investments in private equities (largely reflecting the impact of net losses in real estate investments in the prior year). The increase in Management and other fees primarily reflected the impact of higher average assets under supervision. The increase in Private banking and lending net revenues primarily reflected the impact of the sale of the Marcus loan portfolio in 2023 (including net revenues of approximately $(370) million related to the sale of substantially all of the portfolio) and the impact of higher direct-to-consumer deposit balances. The increase in Incentive fees was driven

> [P4] Operating expenses were $12.66 billion for 2025, 8% higher than 2024, primarily due to higher compensation and benefits expenses. Pre-tax earnings were $4.13 billion for 2025, 15% lower than 2024. 2024 versus 2023. Net revenues in Asset & Wealth Management were $16.32 billion for 2024, 15% higher than 2023, primarily reflecting higher Management and other fees and significantly higher net revenues in Investments. In addition, net revenues in Private banking and lending and Incentive fees were higher. The increase in Management and other fees primarily reflected the impact of higher average assets under supervision. The increase in Investments net revenues primarily reflected significantly hi

> [P5] 2024 versus 2023. Net revenues in Global Banking & Markets were $34.94 billion for 2024, 16% higher than 2023. Investment banking fees were $7.73 billion, 24% higher than 2023, primarily reflecting significantly higher net revenues in Debt underwriting, primarily driven by leveraged finance activity, and in Equity underwriting, primarily driven by secondary and initial public offerings. In addition, net revenues in Advisory were higher, reflecting an increase in completed mergers and acquisitions transactions. As of December 2024, our Investment banking fees backlog increased compared with the end of 2023, primarily reflecting higher estimated net revenues from potential advisory transaction

judge: supported

verdict: [ ]

## claim-007  (agent text-141)

**Claim:** Eli Lilly's effective tax rate in fiscal 2025 was 19.8%

> [P1] 2,910 3,280 (11) Income taxes 5,091 2,090 144 Effective tax rate 19.8 % 16.5 % Gross margin as a percent of revenue in 2025 increased 1.7 percentage points compared with 2024, primarily driven by favorable product mix and improved cost of production, partially offset by lower realized prices. Research and development expenses increased 21 percent in 2025, primarily driven by continued investments in our early and late-stage portfolio. Marketing, selling, and administrative expenses increased 29 percent in 2025, primarily driven by promotional efforts supporting ongoing and planned launches.

> [P2] 3,280.4 3,799.8 (14) Asset impairment, restructuring, and other special charges 860.6 67.7 NM Other—net, (income) expense 218.6 (96.7) NM Income taxes 2,090.4 1,314.2 59 Effective tax rate 16.5 % 20.1 % NM - not meaningful Gross margin as a percent of revenue in 2024 increased 2.1 percentage points compared with 2023, primarily driven by favorable product mix and higher realized prices. Research and development expenses increased 18 percent in 2024, primarily driven by continued investments in our early and late-stage portfolio. Marketing, selling, and administrative expenses increased 16 percent in 2024, primarily driven by promotional efforts supporting ongoing and future launches.

> [P3] Membership and other income increased 13.3% and 7.5% for fiscal 2025 and 2024, respectively, when compared to the previous fiscal year. For fiscal 2025 and 2024, the increases were primarily due to growth in membership base and Plus penetration. Fiscal 2025 and 2024 were also positively impacted by the expiration of a promotional offering offsetting membership fee increases during the fourth quarter of fiscal 2024. Gross profit rate increased 37 and 55 basis points for fiscal 2025 and 2024, respectively, when compared to the previous fiscal year. For fiscal 2025, the increase in gross profit rate was primarily due to improved operational efficiencies related to merchandise flow and increased

> [P4] Percent change 43 % 48 % 45 % In the U.S., the volume increase and the lower realized prices in 2025 were primarily driven by Mounjaro and Zepbound. Outside the U.S., the volume increase in 2025 was primarily driven by Mounjaro. The following table summarizes our revenue, including net product revenue and collaboration and other revenue, by product in 2025 compared with 2024:

> [P5] Our effective income tax rate was 23.4%, 25.5%, and 33.6% for fiscal 2025, 2024 and 2023, respectively. The decrease in effective tax rate in fiscal 2025 compared to fiscal 2024 is primarily due to the tax impact on changes in fair value of our investments. The higher effective tax rate in fiscal 2023 compared to fiscal 2025 and fiscal 2024 is primarily related to the tax impacts of the separation of Flipkart and PhonePe. Our effective income tax rate may also fluctuate as a result of various factors, including changes in our assessment of unrecognized tax benefits, valuation allowances, business operations, acquisitions, investments, entry into new businesses and geographies, intercompany t

> [P6] 36. Table of Contents Alphabet Inc. Provision for Income Taxes The following table presents provision for income taxes (in millions, except effective tax rate): Year Ended December 31, 2024 2025 Income before provision for income taxes $ 119,815 $ 158,826 Provision for income taxes $ 19,697 $ 26,656 Effective tax rate 16.4 % 16.8 % The effective tax rate increased from 2024 to 2025. This increase was primarily due to a decrease in the US Federal Foreign Derived Intangible Income tax deduction, a non-deductible EC fine and legal settlement in the US, partially offset by changes in prior period tax positions. Changes to US tax law enacted on July 4, 2025, allow for immediate expensing of domes

> [F1] ticker = LLY, fiscal_year = 2024, effective_tax_rate = N/A, explanation = The requested metrics (Income Tax Expense and Pre-tax Income) are not available in the provided financial_facts table, therefore the effective tax rate and its year-over-year drivers cannot be calculated.

> [F2] ticker = LLY, fiscal_year = 2025, effective_tax_rate = N/A, explanation = The requested metrics (Income Tax Expense and Pre-tax Income) are not available in the provided financial_facts table, therefore the effective tax rate and its year-over-year drivers cannot be calculated.

judge: supported

verdict: [ ]

## claim-008  (agent text-107)

**Claim:** Apple employs encryption, authentication technologies, and multifactor authentication to protect against unauthorized access

> [P1] The Company has implemented systems and processes intended to secure its information technology systems and prevent unauthorized access to or loss of sensitive data, and mitigate the impact of unauthorized access, including through the use of encryption and authentication technologies. As with all companies, these security measures may not be sufficient for all eventualities and are vulnerable to hacking, ransomware attacks, employee error, malfeasance, system error, faulty password management or other irregularities. For example, third parties can fraudulently induce the Company’s or its suppliers’ and other third parties’ employees or customers into disclosing usernames, passwords or other

> [P2] As with all companies, the security the Company has implemented may not be sufficient for all eventualities and are vulnerable to hacking, ransomware attacks, employee error, malfeasance, system error, faulty password management or other irregularities. For example, third parties can fraudulently induce the Company’s or its suppliers’ and other third parties’ employees or customers into disclosing usernames, passwords or other sensitive information, which can, in turn, be used for unauthorized access to the Company’s or such suppliers’ or third parties’ systems and services. To help protect customers and the Company, the Company deploys and makes available technologies like multifactor authe

> [P3] The Company’s business and reputation are impacted by information technology system failures and network disruptions. The Company and its global supply chain are dependent on complex information technology systems and are exposed to information technology system failures or network disruptions caused by natural disasters, accidents, power disruptions, telecommunications failures, acts of terrorism or war, computer viruses, physical or electronic break-ins, ransomware or other cybersecurity incidents, or other events or disruptions. System upgrades, redundancy and other continuity measures may be ineffective or inadequate, and the Company’s or its vendors’ business continuity and disaster rec

> [P4] The Company’s business and reputation are impacted by information technology system failures and network disruptions. The Company and its global supply chain are dependent on complex information technology systems and are exposed to information technology system failures or network disruptions caused by natural disasters, accidents, power disruptions, telecommunications failures, acts of terrorism or war, computer viruses, physical or electronic break-ins, ransomware or other cybersecurity incidents, or other events or disruptions. System upgrades, redundancy and other continuity measures may be ineffective or inadequate, and the Company’s or its vendors’ business continuity and disaster rec

> [P5] The Company’s global operations are subject to complex and changing laws and regulations worldwide on subjects including antitrust; privacy, data security and data localization; online safety; age verification; consumer protection; advertising, sales, billing and e-commerce; financial services and technology; product liability; intellectual property ownership and infringement; digital platforms; machine learning and artificial intelligence; internet, telecommunications and mobile communications; media, television, film and digital content; availability of third-party software applications and services; labor and employment; anticorruption; import, export and trade; foreign exchange controls

> [P6] The Company’s business also requires it to share confidential information with suppliers and other third parties. The Company relies on global suppliers that are also exposed to ransomware and other malicious attacks that can disrupt business operations. Although the Company takes steps to secure confidential information that is provided to or accessible by third parties working on the Company’s behalf, such measures are not always effective and losses or unauthorized access to, or releases of, confidential information occur. Such incidents and other malicious attacks could materially adversely affect the Company’s business, reputation, results of operations, financial condition and stock pr

judge: supported

verdict: [ ]

## claim-009  (baseline text-129)

**Claim:** The increase was driven by significantly higher net revenues in Equities intermediation, primarily due to derivatives.

> [P1] Goldman Sachs 2025 Form 10-K THE GOLDMAN SACHS GROUP, INC. AND SUBSIDIARIES Management’s Discussion and Analysis Net revenues in Equities were $13.43 billion, 16% higher than 2023, reflecting significantly higher net revenues in Equities intermediation, primarily driven by derivatives, and higher net revenues in Equities financing, driven by prime financing. Net revenues in Other were $561 million for 2024, compared with $80 million for 2023, with the increase primarily reflecting significantly lower net losses on hedges. Provision for credit losses was $84 million for 2024, compared with $430 million for 2023. Provisions for 2023 primarily reflected net provisions related to the commercial

> [P2] The increase in FICC intermediation net revenues reflected the impact of improved market-making conditions on our inventory, partially offset by lower client activity. The following provides information about our FICC intermediation net revenues by business, compared with results for 2023: •Net revenues in currencies, mortgages and credit products reflected the impact of improved market-making conditions on our inventory. •Net revenues in interest rate products and commodities primarily reflected lower client activity. Net revenues in Equities were $13.43 billion, 16% higher than 2023, reflecting significantly higher net revenues in Equities intermediation, primarily driven by derivatives, a

> [P3] The increase in Equity investments net revenues primarily reflected significantly higher net gains from investments in private equities (largely reflecting the impact of net losses in real estate investments in the prior year). The increase in Management and other fees primarily reflected the impact of higher average assets under supervision. The increase in Private banking and lending net revenues primarily reflected the impact of the sale of the Marcus loan portfolio in 2023 (including net revenues of approximately $(370) million related to the sale of substantially all of the portfolio) and the impact of higher direct-to-consumer deposit balances. The increase in Incentive fees was driven

> [P4] Operating expenses were $12.66 billion for 2025, 8% higher than 2024, primarily due to higher compensation and benefits expenses. Pre-tax earnings were $4.13 billion for 2025, 15% lower than 2024. 2024 versus 2023. Net revenues in Asset & Wealth Management were $16.32 billion for 2024, 15% higher than 2023, primarily reflecting higher Management and other fees and significantly higher net revenues in Investments. In addition, net revenues in Private banking and lending and Incentive fees were higher. The increase in Management and other fees primarily reflected the impact of higher average assets under supervision. The increase in Investments net revenues primarily reflected significantly hi

> [P5] 2024 versus 2023. Net revenues in Global Banking & Markets were $34.94 billion for 2024, 16% higher than 2023. Investment banking fees were $7.73 billion, 24% higher than 2023, primarily reflecting significantly higher net revenues in Debt underwriting, primarily driven by leveraged finance activity, and in Equity underwriting, primarily driven by secondary and initial public offerings. In addition, net revenues in Advisory were higher, reflecting an increase in completed mergers and acquisitions transactions. As of December 2024, our Investment banking fees backlog increased compared with the end of 2023, primarily reflecting higher estimated net revenues from potential advisory transaction

judge: supported

verdict: [ ]

## claim-010  (baseline text-092)

**Claim:** Additionally, for product liability claims incurred but not filed, the company accrues amounts based primarily on historical claims experience and data regarding product usage.

> [P1] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P2] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P3] We are subject to a substantial number of claims, litigation, and investigations involving various current and historical products and practices. These claims relate to how we commercialize and/or how we price our products, product safety, our operations as well as contractual matters and other disputes. We have also filed lawsuits and taken other legal actions to protect our intellectual property and address unlawful practices. See Item 8, "Financial Statements and Supplementary Data—Note 16: Contingencies," for more information on certain matters. Like many companies in our industry, from time to time investigations into aspects of our business include inquiries, subpoenas, and other types

> [P4] initiated enforcement or other actions across industries to seek alignment with policy initiatives. Because of the nature of pharmaceutical products and our evolving business, we are, and could increasingly become, subject to large numbers of product liability claims for our previous, current, or future products, or to further litigation or investigations, including related to product safety, marketing, pricing, or other commercial practices. Some of these matters involve or may involve numerous plaintiffs and parties seeking large or indeterminate financial claims and may remain unresolved for several years. Such matters could negatively impact our reputation, affect our results of operatio

> [P5] We derive a significant percentage of our total revenue from relatively few products and sell our products through consolidated supply chain entities, which subjects us to various risks. We derived direct product and/or collaboration and other revenues of more than $3 billion for each of Mounjaro, Zepbound, Verzenio, Trulicity, Taltz, and Jardiance (including Glyxambi, Synjardy, and Trijardy XR) that collectively accounted for 82 percent of our total revenues in 2025. In particular, Mounjaro and Zepbound accounted for 56 percent of our total revenues in 2025, and we expect cardiometabolic health products will continue to represent a significant and growing portion of our business, revenues,

judge: supported

verdict: [ ]

## claim-011  (agent text-091)

**Claim:** Procter & Gamble's Grooming segment includes the Pre- and Post-Shave Products product line.

> [P1] Family Care (Paper Towels, Tissues, Toilet Paper) Bounty, Charmin, Puffs (1)Percent of Net sales and Net earnings for the fiscal year ended June 30, 2025 (excluding results held in Corporate). (2)Effective July 1, 2024, the Beauty reportable business segment separated Skin and Personal Care into individual operating segments, Skin Care and Personal Care. This transition included separation of the management team, strategic decision-making, innovation plans, financial targets, budgets and management reporting. Organization Design: Sector Business Units Beauty: The beauty categories in which we compete are hair care, personal care and skin care. We are a global market leader in the retail hair

> [P2] Skin Care (2) (Facial Moisturizers, Cleaners and Treatments) Olay, SK-II Grooming 8% 10% Grooming (Appliances, Female Blades & Razors, Male Blades & Razors, Pre- and Post-Shave Products, Other Grooming) Braun, Gillette, Venus Health Care 14% 15% Oral Care (Toothbrushes, Toothpastes, Other Oral Care) Crest, Oral-B Personal Health Care (Gastrointestinal, Pain Relief, Rapid Diagnostics, Respiratory, Vitamins/Minerals/Supplements, Other Personal Health Care) Metamucil, Neurobion, Pepto-Bismol, Vicks Fabric & Home Care 36% 35% Fabric Care (Fabric Enhancers, Laundry Additives, Laundry Detergents) Ariel, Downy, Gain, Tide

> [P3] The Company's product categories are organized into five SBUs and five reportable segments (under U.S. GAAP): Beauty; Grooming; Health Care; Fabric & Home Care; and Baby, Feminine & Family Care. The SBUs are responsible for global brand strategy, product upgrades and innovation, marketing plans and supply chain. They have direct profit responsibility for markets (referred to as Focus Markets) representing the large majority of the Company's sales and earnings and are also responsible for innovation plans, supply plans and operating frameworks to drive growth and value creation in the remaining markets (referred to as Enterprise Markets). Throughout the MD&A, we reference business results by

> [P4] The Company's product categories are organized into five SBUs and five reportable segments (under U.S. GAAP): Beauty; Grooming; Health Care; Fabric & Home Care; and Baby, Feminine & Family Care. The SBUs are responsible for global brand strategy, product upgrades and innovation, marketing plans and supply chain. They have direct profit responsibility for markets (referred to as Focus Markets) representing the large majority of the Company's sales and earnings and are also responsible for innovation plans, supply plans and operating frameworks to drive growth and value creation in the remaining markets (referred to as Enterprise Markets). Throughout the MD&A, we reference business results by

> [P5] Olay, SK-II Grooming 8% 9% Grooming (Appliances, Female Blades & Razors, Male Blades & Razors, Pre- and Post-Shave Products, Other Grooming) Braun, Gillette, Venus Health Care 14% 15% Oral Care (Toothbrushes, Toothpastes, Other Oral Care) Crest, Oral-B Personal Health Care (Gastrointestinal, Pain Relief, Rapid Diagnostics, Respiratory, Vitamins/Minerals/Supplements, Other Personal Health Care) Metamucil, Neurobion, Pepto-Bismol, Vicks Fabric & Home Care 35% 35% Fabric Care (Fabric Enhancers, Laundry Additives, Laundry Detergents) Ariel, Downy, Gain, Tide Home Care (Air Care, Dish Care, P&G Professional, Surface Care) Cascade, Dawn, Fairy, Febreze, Mr. Clean, Swiffer Baby, Feminine & Family C

> [P6] Always, Always Discreet, Tampax Family Care (Paper Towels, Tissues, Toilet Paper) Bounty, Charmin, Puffs (1)Percent of Net sales and Net earnings for the fiscal year ended June 30, 2026 (excluding results held in Corporate). Organization Design: Sector Business Units Beauty: The beauty categories in which we compete are hair care, personal care and skin care. We are a global market leader in the retail hair care market with about 20% global market share primarily behind our Head & Shoulders and Pantene brands. In personal care, we have the number two market share position with about 20% global market share, primarily behind our Old Spice, Native, Secret and Safeguard brands. In skin care, th

judge: supported

verdict: [ ]

## claim-012  (baseline cross-172)

**Claim:** Working capital and other impacts consumed $2.5 billion of cash in fiscal 2025

> [P1] The Procter & Gamble Company 25 complement our portfolio of businesses, brands and geographies. As necessary, we may supplement operating cash flow with debt to fund these activities. The overall cash position of the Company reflects our strong business results and a global cash management strategy that takes into account liquidity management, economic factors and tax considerations. Cash Flow Analysis ($ millions) 2025 2024 Net cash provided by operating activities $ 17,817 $ 19,846 Net cash used in investing activities (3,818) (3,504) Net cash used in financing activities (14,036) (14,855) Adjusted Free Cash Flow 14,606 16,946 Adjusted Free Cash Flow Productivity 87 % 105 % Operating Cash

> [P2] We define free cash flow as net cash provided by operating activities in a period minus payments for property and equipment made in that period. We had net cash provided by operating activities of $36.4 billion, $35.7 billion and $28.8 billion for fiscal 2025, 2024 and 2023, respectively. We generated free cash flow of $12.7 billion, $15.1 billion and $12.0 billion for fiscal 2025, 2024 and 2023, respectively. The increase in net cash provided by operating activities in fiscal 2025 is primarily due to an increase in cash provided by operating income and lapping the payment of accrued opioid legal charges in the prior year, partially offset by increased inventory purchases. Free cash flow for

> [P3] In June 2025, the Company announced a two-year portfolio and productivity plan to streamline its portfolio and organization to improve its cost structure and competitiveness. In fiscal 2026, the Company incurred incremental restructuring charges of $903 million after tax under the program. Restructuring accruals of $336 million as of June 30, 2026, are classified as current liabilities. Approximately 67% of the before tax restructuring charges incurred in fiscal 2026 either have been or will be settled with cash. Consistent with our policies for restructuring-type activities, the resulting charges are funded by and included within Corporate for segment reporting. Savings generated from the C

> [P4] 30 The Procter & Gamble Company supplemental understanding of underlying sales trends by providing sales growth on a consistent basis. This measure is used in assessing the achievement of management goals for at-risk compensation. The following tables provide a numerical reconciliation of net sales growth to organic sales growth: Fiscal year ended June 30, 2025 Net Sales Growth Foreign Exchange Impact Acquisition & Divestiture Impact/Other (1) Organic Sales Growth Beauty (2) % 1 % 2 % 1 % Grooming — % 2 % — % 2 % Health Care 2 % 1 % — % 3 % Fabric & Home Care — % 1 % 1 % 2 % Baby, Feminine & Family Care — % 1 % — % 1 % TOTAL COMPANY — % 1 % 1 % 2 % (1)Acquisition & Divestiture Impact/Other i

> [P5] Machinery, Power & Energy Net cash provided by operating activities was $12.278 billion in 2025, compared with $11.437 billion in 2024. The increase was primarily due to lower working capital requirements and lower cash taxes paid. These were partially offset by lower profit before taxes, adjusted for non-cash items. Within working capital, changes in customer advances, accounts payable, and accrued wages, salaries, and employee benefits favorably impacted cash flow, partially offset by changes in inventories and receivables. Net cash used by investing activities in 2025 was $2.870 billion, compared with net cash provided of $133 million in 2024. The change was primarily due to lower proceed

judge: supported

verdict: [ ]

## claim-013  (baseline text-110)

**Claim:** Concerns about the high absolute energy requirements of NVIDIA's GPUs could negatively impact its business

> [P1] Our business and those of our suppliers and customers is subject to sustainability-related laws, regulations and lawsuits. New or proposed regulations relating to carbon taxes, fuel or energy taxes, pollution limits, sustainability-related disclosure and governance and supply chain governance could result in greater direct costs, including costs associated with changes to manufacturing processes or the procurement of raw materials used in manufacturing processes, increased capital expenditures to improve facilities and equipment, higher compliance and energy costs to reduce emissions, other compliance costs, and greater indirect costs resulting from our customers and/or suppliers incurring a

> [P2] Our business and those of our suppliers and customers may also be subject to climate-related laws, regulations and lawsuits. New or proposed regulations relating to carbon taxes, fuel or energy taxes, pollution limits, sustainability-related disclosure and governance and supply chain governance could result in greater direct costs, including costs associated with changes to manufacturing processes or the procurement of raw materials used in manufacturing processes, increased capital expenditures to improve facilities and equipment, higher compliance and energy costs to reduce emissions, other compliance costs, and greater indirect costs resulting from our customers and/or suppliers incurring

> [P3] Compliance with laws, rules, and regulations has not otherwise had a material effect upon our capital expenditures, results of operations, or competitive position and we do not currently anticipate material capital expenditures for environmental control facilities. Compliance with existing or future governmental regulations, including, but not limited to, those pertaining to IP ownership and infringement, taxes, import and export requirements and tariffs, anti-corruption, business acquisitions, foreign exchange controls and cash repatriation restrictions, data privacy requirements, competition and antitrust, advertising, employment, product regulations, cybersecurity, environmental, health a

> [P4] Climate Change In the area of environmental sustainability, we work to address our climate impacts across our product lifecycle and assess related risks, including current and emerging regulations and market impacts. In May 2024, we published metrics related to our environmental impact for fiscal year 2024. Fiscal year 2025 metrics are expected to be published in the first half of fiscal year 2026. There has been no material impact to our capital expenditures, results of operations or competitive position associated with global environmental sustainability regulations, compliance, or costs from sourcing renewable energy. We committed to purchase or generate enough renewable energy to match 1

> [P5] Certain shareholder advocacy groups, investment funds, shareholders and other market participants, customers and government regulators have focused on corporate sustainability practices and disclosures, including those associated with climate change and human rights. Stakeholders may not be satisfied with our corporate sustainability practices and goals or the speed of their adoption. Further, there are state-level initiatives in the U.S. that may differ from other regulatory requirements or our various stakeholders’ expectations. Additionally, our corporate sustainability practices, oversight of our practices or disclosure controls may not meet evolving shareholder, regulator or other indus

judge: supported

verdict: [ ]

## claim-014  (baseline text-088)

**Claim:** Keytruda is approved for adjuvant treatment following resection and platinum-based chemotherapy for certain patients with NSCLC

> [P1] Pharmaceutical The Pharmaceutical segment includes human health pharmaceutical and vaccine products. Human health pharmaceutical products consist of therapeutic and preventive agents, generally sold by prescription, for the treatment of human disorders. Human health vaccine products consist of preventive pediatric, adolescent and adult vaccines. Certain of the products within the Company’s franchises are as follows: Table of Contents Oncology Keytruda is an anti-PD-1 (programmed death receptor-1) therapy that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroeso

> [P2] The Company received more than 25 regulatory approvals in major markets in 2024, including the Winrevair and Capvaxive approvals noted above, along with numerous approvals in oncology. Keytruda received approval for additional indications in the U.S. and/or internationally as monotherapy in the therapeutic areas of hepatocellular carcinoma (HCC), melanoma and urothelial carcinoma, in combination with chemotherapy in the therapeutic areas of biliary tract cancer, cervical cancer, endometrial carcinoma, gastric or gastroesophageal junction (GEJ) adenocarcinoma, malignant pleural mesothelioma and non-small-cell lung cancer (NSCLC), as well as in combination with Padcev (enfortunab vedotin-ejfv)

> [P3] MK-3475, Keytruda, is an anti-PD-1 therapy approved for the treatment of many cancers that is in clinical development for expanded indications. These studies encompass more than 30 cancer types including: biliary, estrogen receptor positive breast, triple-negative breast, cervical, colorectal, endometrial, esophageal, gastric, glioblastoma, head and neck, hepatocellular, Hodgkin lymphoma, non-Hodgkin lymphoma, non-small-cell lung, small-cell lung, melanoma, malignant pleural mesothelioma, ovarian, prostate, renal, and urothelial, several of which are currently in Phase 3 clinical development. Further trials are being planned for other cancers. Keytruda is under review in the EU and Japan for

> [P4] Keytruda (pembrolizumab) is an anti-PD-1 (programmed death receptor-1) therapy available for intravenous administration that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroesophageal junction (GEJ) carcinoma, head and neck squamous cell carcinoma (HNSCC), hepatocellular carcinoma (HCC), melanoma, Merkel cell carcinoma, microsatellite instability-high (MSI-H) or mismatch repair deficient (dMMR) solid tumors (including MSI-H/dMMR colorectal cancer and endometrial carcinoma), non-small cell lung cancer (NSCLC), primary mediastinal large B-cell lymphoma (PMBCL),

> [P5] Disease (JPN) Pneumococcal Vaccine Adult V116 Capvaxive (EU) (JPN) Pulmonary Arterial Hypertension MK-7962 Winrevair (JPN) Respiratory Syncytial Virus MK-1654 (clesrovimab) (U.S.) (EU) Certain Supplemental Filings Cancer MK-3475 Keytruda • First-Line Unresectable Advanced or Metastatic Malignant Pleural Mesothelioma (KEYNOTE-483) (EU) (JPN) MK-6482 Welireg • Advanced, Unresectable, or Metastatic Pheochromocytoma and Paraganglioma (LITESPARK-015) (U.S.) Footnotes: (1) Being developed in a collaboration. (2) Being developed in combination with Keytruda. (3) Being developed as monotherapy and/or in combination with Keytruda. (4) FDA lifted clinical hold on December 4, 2024. (5) On FDA partial c

judge: supported

verdict: [ ]

## claim-015  (agent text-157)

**Claim:** Ultimately, these factors can harm Alphabet's business, reputation, financial condition, and operating results.

> [P1] Further, we are subject to evolving laws and regulations that dictate whether, how, and under what circumstances we can transfer, process, or receive personal data, as well as ongoing enforcement actions from supervisory authorities related to cross-border transfers of personal data. The validity of various data transfer mechanisms we currently rely upon remains subject to legal, regulatory, and political developments globally, which may require us to adapt our existing arrangements. We face, and may continue to face, intellectual property infringement or misappropriation, violation of rights of publicity, and other claims that could be costly to defend, result in significant damage awards o

> [P2] 21. Table of Contents Alphabet Inc. Further, we are subject to evolving laws and regulations that dictate whether, how, and under what circumstances we can transfer, process and/or receive personal data, as well as ongoing enforcement actions from supervisory authorities related to cross-border transfers of personal data. The validity of various data transfer mechanisms we currently rely upon remains subject to legal, regulatory, and political developments globally, which may require us to adapt our existing arrangements. We face, and may continue to face, intellectual property infringement or misappropriation, violation of rights of publicity, and other claims that could be costly to defend

> [P3] Our international operations expose us to additional risks that could harm our business, reputation, financial condition, and operating results. 14. Table of Contents Alphabet Inc. Our international operations are significant to our revenues and net income, and we plan to continue to grow internationally. International revenues accounted for approximately 51% of our consolidated revenues in 2024. In addition to risks described elsewhere in this section, our international operations expose us to other risks, including the following: •restrictions on foreign ownership and investments, and stringent foreign exchange controls that might prevent us from repatriating cash earned in countries outsi

> [P4] of data protection laws, imposing specific obligations with respect to the processing of personal data, including required notices, consents, and opt-outs. Further, the increased risk of inadvertent disclosure of confidential information or personal data in connection with the utilization of AI technologies may result in stronger regulatory scrutiny, leading to legal and regulatory investigations and enforcement actions that could harm our business, even if unfounded. Adverse legal rulings, legislation, or regulation have resulted in, and may continue to result in, fines and orders requiring that we change our practices, which have had and could continue to have an adverse effect on how we p

> [P5] Our operations and financial results are subject to various risks and uncertainties, including but not limited to those described below, which could harm our business, reputation, financial condition, and operating results, and affect the trading price of our Class A and Class C stock. Risks Specific to our Company We generate a significant portion of our revenues from advertising. Reduced spending by advertisers, a loss of partners, or new and existing technologies that block ads online and/or affect our ability to personalize ads could harm our business. We generated more than 75% of total revenues from online advertising in 2024. Many of our advertisers, companies that distribute our prod

> [P6] Authorities around the world have adopted and are considering a number of legislative and regulatory proposals concerning data protection, data usage and portability, and encryption of user data. Additionally, the increasing adoption of AI technologies, which rely on the collection of large amounts of data and use of such data for training purposes, has led data protection authorities around the world to consider and adopt new and evolving interpretations of data protection laws, imposing specific obligations with respect to the processing of personal data, including required notices, consents, and opt-outs. Further, the increased risk of inadvertent disclosure of confidential information or

judge: supported

verdict: [ ]

## claim-016  (baseline text-075)

**Claim:** If AI products are utilized in unintended ways, violate the law, or harm individuals or businesses, Microsoft may face legal claims or enforcement actions that could damage its reputation.

> [P1] Ineffective or inadequate AI development or deployment practices by Microsoft or others could result in incidents that impair the acceptance of AI solutions, cause harm to individuals, customers, or society, or result in our products and services not working as intended. Human review of certain inputs and outputs or other forms of human oversight may be required, including for agentic AI systems that can take actions autonomously. Companion or highly-personalized AI systems may result in over-reliance or dependence by users that is harmful. Our implementation of AI systems could result in legal liability, regulatory action, litigation, brand, reputational, or competitive harm, or other adver

> [P2] Our products and services, how they are used by customers, and how third-party products and services interact with them, may present security, privacy, and execution risks. Our products and services may contain defects in design, manufacture, or operation that make them insecure or ineffective for their intended purposes. For example, customers control our products and services, including our AI products, within their environments, and may deploy them in high-risk scenarios or utilize them inappropriately. Our products may also collect large amounts of data in manners which may not satisfy customers or regulatory requirements. Our customers also operate complex systems with third-party hardw

> [P3] We have experienced, and expect to continue to experience, instances in which the AI solutions we enable or offer produce unintended consequences, are used or customized in unforeseen ways by customers or partners, or operate in a manner inconsistent with our responsible AI policies and practices. These outcomes may give rise to public controversy, societal concerns, or regulatory actions relating to human rights, privacy, employment, or other social, economic, or political issues, and could adversely affect our reputation, competitive position, business, financial condition, and results of operations. OPERATIONAL RISKS We may be unable to develop and expand adequate infrastructure. Our incr

> [P4] •We are subject to complex laws, rules, regulations, and political and other actions, including restrictions on the export of our products, which may adversely impact our business. •Scrutiny regarding our corporate sustainability practices could result in financial, reputational, or operational harm and liability. •Issues relating to the responsible use of our technologies, including AI, may result in reputational or financial harm and liability. •Adequately protecting our IP rights could be costly, and our ability to compete could be harmed if we are unsuccessful or if we are prohibited from making or selling our products. •We are subject to stringent and changing data privacy and security

> [P5] Ineffective or inadequate AI development or deployment practices by Microsoft or others could result in incidents that impair the acceptance of AI solutions, cause harm to individuals, customers, or society, or result in our products and services not working as intended. Human review of certain inputs and outputs may be required, including for agentic AI systems that can take actions autonomously. Our implementation of AI systems could result in legal liability, regulatory action, brand, reputational, or competitive harm, or other adverse impacts. These risks may stem from issues related to intellectual property, data privacy, and other claims associated with AI training and outputs.

judge: supported

verdict: [ ]

## claim-017  (agent sql-049)

**Claim:** Merck's cash provided by operating activities in fiscal 2024 was $21.468 billion

> [F1] ticker = MRK, fiscal_year = 2024, metric = operating_cash_flow, value = 21468000000.0

judge: supported

verdict: [ ]

## claim-018  (agent cross-199)

**Claim:** The MD&A attributes the year‑over‑year decline in cash provided by operating activities to more normalized inventory levels during fiscal 2024 versus the strategic reductions in inventory during fiscal 2023 within the Primary segment

> [P1] Cash flow generated from operations provides us with a significant source of liquidity. Our operating cash flows result primarily from cash received from our customers, offset by cash payments we make for products and services, associate compensation, operations, occupancy costs, and income taxes. Cash provided by or used in operating activities is also subject to changes in working capital. Working capital at any point in time is subject to many variables, including seasonality, inventory management and category expansion, the timing of cash receipts and payments, vendor payment terms, and fluctuations in foreign exchange rates. Net cash provided by operating activities decreased by $1.4 bi

> [P2] We have no material off-balance sheet arrangements. CASH FLOWS SUMMARY Operating Activities Cash flow generated from operations provides us with a significant source of liquidity. Our operating cash flows result primarily from cash received from our customers, offset by cash payments we make for products and services, associate compensation, operations, occupancy costs, and income taxes. Cash provided by or used in operating activities is also subject to changes in working capital. Working capital at any point in time is subject to many variables, including seasonality, inventory management and category expansion, the timing of cash receipts and payments, vendor payment terms, and fluctuatio

> [P3] TARGET CORPORATION 2024 Form 10-K 31 MANAGEMENT'S DISCUSSION AND ANALYSIS Table of Contents ANALYSIS OF FINANCIAL CONDITION Index to Financial Statements Analysis of Financial Condition Liquidity and Capital Resources Capital Allocation We follow a disciplined and balanced approach to capital allocation based on the following priorities, ranked in order of importance: first, we fully invest in opportunities to profitably grow our business, create sustainable long-term value, and maintain our current operations and assets; second, we maintain a competitive quarterly dividend and seek to grow it annually; and finally, we return any excess cash to shareholders by repurchasing shares within the

> [P4] The following discussion provides an analysis of the Company’s financial condition and results of operations from management's perspective and should be read in conjunction with the consolidated financial statements and related notes included in this report. The discussion in this Form 10-K generally focuses on fiscal 2024 compared to fiscal 2023. A discussion of our results of operations and changes in financial condition for fiscal 2023 compared to fiscal 2022 has been omitted from this report, but can be found in Part II, Item 7. Management’s Discussion and Analysis of Financial Condition and Results of Operations of our Form 10-K for fiscal 2023. TABLE OF CONTENTS Executive Summary Resul

> [P5] 40. Table of Contents Alphabet Inc. expenses. Additionally, a decrease in the 2024 U.S. federal Foreign Derived Intangible Income tax deduction contributed to an increase in the effective tax rate. These factors were partially offset by an increase in stock-based compensation-related tax benefits in 2024. The OECD is coordinating negotiations among more than 140 countries with the goal of achieving consensus around substantial changes to international tax policies, including the implementation of a minimum global effective tax rate of 15%. Some countries have already implemented the legislation effective January 1, 2024, and we expect others to follow, however this did not have a material ef

> [P6] Gross profit increased $2.3 billion, or 4.6%, to $53.3 billion in fiscal 2024. Gross profit as a percent of net sales, or gross profit margin, was 33.4% for both fiscal 2024 and fiscal 2023, and primarily reflected lower transportation costs and lower shrink within our Primary segment, offset by the inclusion of SRS in our consolidated results. Operating Expenses Our operating expenses are composed of SG&A and depreciation and amortization. Selling, General & Administrative. SG&A increased $2.2 billion, or 8.1%, to $28.7 billion in fiscal 2024. As a percent of net sales, SG&A was 18.0% in fiscal 2024 compared to 17.4% in fiscal 2023, which primarily reflects higher payroll costs, deleverage

judge: supported

verdict: [ ]

## claim-019  (baseline text-117)

**Claim:** Earnings increased by $63 million due to lower depreciation, depletion and amortization (DD&A) driven by year‑end 2024 upward reserve revisions.

> [P1] The Canada segment operations include the Surmont oil sands development in Alberta, the Montney unconventional play in British Columbia and commercial operations. In 2025, Canada contributed nine percent of our consolidated liquids production and five percent of our consolidated natural gas production. Net Income (Loss) Canada reported earnings of $741 million in 2025 compared with earnings of $712 million in 2024. Increases to earnings included higher revenues resulting from higher volumes of $142 million and the timing of sales as compared with 2024 partly offset by lower commodity prices of $303 million. Increases to earnings included lower DD&A of $63 million driven by year-end 2024 upwa

> [P2] Net Income (Loss) The Europe, Middle East and North Africa segment reported earnings of $1,224 million in 2025 compared with earnings of $1,189 million in 2024. Earnings in 2025 included higher revenues resulting from higher volumes of $296 million, including volumes from our Equatorial Guinea assets from the acquisition of Marathon Oil, partly offset by lower overall realized commodity prices of $185 million, driven by lower crude prices. See Note 3. Decreases to earnings included higher production and operating expenses of $88 million, primarily from our acquisition of Marathon Oil. See Note 3. Consolidated Production Average consolidated production increased 40 MBOED in 2025, compared wit

> [P3] Millions of Dollars Years Ended December 31 2025 2024 2023 Sales and other operating revenues $ 58,944 54,745 56,141 Equity in earnings of affiliates 1,335 1,705 1,720 Gain (loss) on dispositions 731 51 228 Purchased commodities 22,325 20,012 21,975 Production and operating expenses 10,331 8,751 7,693 Selling, general and administrative expenses 893 1,158 705 Depreciation, depletion and amortization 11,500 9,599 8,270 Other expenses 20 181 2 Income tax provision (benefit) 4,668 4,427 5,331 Sales and other operating revenues increased $4,199 million in 2025, primarily due to higher volumes of $6,197 million, inclusive of sales volumes from our acquisition of Marathon Oil and higher realized g

> [P4] The Canada segment operations include the Surmont oil sands development in Alberta, the Montney unconventional play in British Columbia and commercial operations. In 2024, Canada contributed ten percent of our consolidated liquids production and five percent of our consolidated natural gas production. Net Income (Loss) Canada reported earnings of $712 million in 2024 compared with earnings of $402 million in 2023. Earnings included higher revenues resulting from higher volumes of $676 million; driven by our increased working interest in Surmont of $584 million and new wells online in the Montney of $180 million, partially offset by planned turnaround activity at Surmont impacting revenues by

> [P5] Operating expenses as a percentage of segment net sales decreased 5 and 152 basis points for fiscal 2025 and 2024, respectively, when compared to the previous fiscal year. The decrease in operating expenses as a percentage of segment net sales for fiscal 2025 was primarily due to increased sales driving expense leverage, partially offset by planned investments in associate wages and strategic priorities in Mexico and Central America. The decrease in operating expenses as a percentage of segment net sales for fiscal 2024, was primarily due to the lapping of business reorganization and restructuring charges incurred related to Flipkart and Massmart in fiscal 2023 and an increase in sales in fi

judge: supported

verdict: [ ]

## claim-020  (baseline sql-036)

**Claim:** Coca-Cola's capital expenditures for fiscal year 2023 were $1,852 million

> [P1] Year Ended December 31, 2024 2023 Capital expenditures $ 2,064 $ 1,852 Europe, Middle East & Africa 0.8 % 2.3 % Latin America — — North America 29.2 22.3 Asia Pacific 0.9 1.2 Global Ventures 9.9 10.4 Bottling Investments 35.6 45.5 Corporate 23.6 18.3

> [P2] In 2024, purchases of investments were $5,640 million and proceeds from disposals of investments were $6,589 million, resulting in a net cash inflow of $949 million. In 2023, purchases of investments were $6,698 million and proceeds from disposals of investments were $4,354 million, resulting in a net cash outflow of $2,344 million. This activity primarily represents the purchases of, and proceeds from the disposals of, investments in marketable securities and short-term investments that were made as part of the Company’s overall cash management strategy. Also included in this activity are purchases of, and proceeds from the disposals of, investments held by our captive insurance companies.

> [P3] Year Ended December 31, 2025 2024 Capital expenditures $ 2,112 $ 2,064 EMEA 11.2 % 10.7 % Latin America 0.1 — North America 31.7 29.2 Asia Pacific 3.4 0.9 Bottling Investments 25.9 35.6 Corporate 27.7 23.6 Collateral (Paid) Received Associated with Hedging Activities — Net Collateral received associated with our hedging activities during the years ended December 31, 2025 and 2024 was $330 million and $235 million, respectively. Refer to Note 5 of Notes to Consolidated Financial Statements for additional information on our hedging activities. Other Investing Activities During the years ended December 31, 2025 and 2024, the total cash inflow from other investing activities was $91 million and

> [P4] The Company has a trade accounts receivable factoring program in certain countries. Under this program, we can elect to sell trade accounts receivables to unaffiliated financial institutions at a discount. In these factoring arrangements, for ease of administration, the Company collects customer payments related to the factored receivables and remits those payments to the financial institutions. The Company sold $21,873 million and $17,704 million of trade accounts receivables under this program during the years ended December 31, 2024 and 2023, respectively. The costs of factoring such receivables were $114 million and $83 million for the years ended December 31, 2024 and 2023, respectively

> [P5] In 2025, purchases of investments were $6,160 million and proceeds from disposals of investments were $4,665 million, resulting in a net cash outflow of $1,495 million. In 2024, purchases of investments were $5,640 million and proceeds from disposals of investments were $6,589 million, resulting in a net cash inflow of $949 million. This activity primarily represents the purchases of, and proceeds from the disposals of, investments in marketable securities and short-term investments that were made as part of the Company’s overall cash management strategy. Also included in this activity are purchases of, and proceeds from the disposals of, investments held by our captive insurance companies.

judge: supported

verdict: [ ]

## claim-021  (agent text-156)

**Claim:** Gains on dispositions increased by $680 million, primarily due to the divestitures of the Ursa and Europa fields, the Ursa Oil Pipeline Company LLC, and other noncore assets in the Lower 48 segment

> [P1] Millions of Dollars Years Ended December 31 2025 2024 2023 Sales and other operating revenues $ 58,944 54,745 56,141 Equity in earnings of affiliates 1,335 1,705 1,720 Gain (loss) on dispositions 731 51 228 Purchased commodities 22,325 20,012 21,975 Production and operating expenses 10,331 8,751 7,693 Selling, general and administrative expenses 893 1,158 705 Depreciation, depletion and amortization 11,500 9,599 8,270 Other expenses 20 181 2 Income tax provision (benefit) 4,668 4,427 5,331 Sales and other operating revenues increased $4,199 million in 2025, primarily due to higher volumes of $6,197 million, inclusive of sales volumes from our acquisition of Marathon Oil and higher realized g

> [P2] Net Income (Loss) Lower 48 reported earnings of $5,264 million in 2025, compared with earnings of $5,175 million in 2024. Increases to earnings included higher revenues resulting from higher volumes of $3,890 million, inclusive of volumes from our acquisition of Marathon Oil, partly offset by lower commodity prices of $1,999 million, driven by lower crude prices. Additional increases included higher gains on dispositions of $494 million, primarily associated with the divestitures of the Ursa and Europa fields and Ursa Oil Pipeline Company LLC, and other noncore assets. Decreases to earnings included higher DD&A of $1,330 million and higher production and operating expenses of $875 million, p

> [P3] Net Income (Loss) The Europe, Middle East and North Africa segment reported earnings of $1,224 million in 2025 compared with earnings of $1,189 million in 2024. Earnings in 2025 included higher revenues resulting from higher volumes of $296 million, including volumes from our Equatorial Guinea assets from the acquisition of Marathon Oil, partly offset by lower overall realized commodity prices of $185 million, driven by lower crude prices. See Note 3. Decreases to earnings included higher production and operating expenses of $88 million, primarily from our acquisition of Marathon Oil. See Note 3. Consolidated Production Average consolidated production increased 40 MBOED in 2025, compared wit

> [P4] Crude and bitumen prices were lower through 2025 as global oil supplies increased faster than global oil demand. Natural gas prices increased due to stronger demand and lower inventory levels relative to 2024. Our worldwide annual average realized price decrease was driven by lower crude and bitumen prices. ConocoPhillips 2025 10-K Management’s Discussion and Analysis Table of Contents Key Operating and Financial Summary Significant items during 2025 and recent announcements included the following: •Reported fourth-quarter 2025 earnings per share of $1.17; •Generated cash provided by operating activities of $19.8 billion; •Distributed $9.0 billion to shareholders, including $5.0 billion thro

> [P5] At December 31, 2025, we had cash and cash equivalents of $6.5 billion, short-term investments of $0.5 billion, and available borrowing capacity under our credit facility of $5.5 billion, totaling approximately $12.5 billion of liquidity. In addition, we have long-term investments in debt securities of $1.1 billion. We believe current cash balances and cash generated by operations, together with access to external sources of funds as described below in the “Significant Changes in Capital” section, will be sufficient to meet our funding requirements in the near- and long-term, including our capital spending program, capital return program and required debt payments. Significant Changes in Cap

> [P6] Net Income (Loss) Asia Pacific reported earnings of $1,167 million in 2025, compared with $1,724 million in 2024. Decreases to earnings included lower revenues resulting from lower commodity prices of $206 million. Additional decreases to earnings included lower earnings from equity affiliates of $271 million, primarily due to lower LNG sales prices and higher exploration expenses of $64 million, primarily driven by dry hole expenses associated with certain wells in Malaysia and Australia. Consolidated Production Average consolidated production increased three MBOED in 2025, compared with 2024. Increases to production were primarily due to development activity in Bohai Bay in China and Gumus

judge: supported

verdict: [ ]

## claim-022  (baseline text-086)

**Claim:** Reimbursement or other costs

> [P1] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P2] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P3] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions, fires, product spills, severe weather, geological events, global health crises, such as epidemics and pandemics, labor disputes, geopolitical tensions, armed hostilities, terrorist or piracy attacks, sabotage, civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater technological challen

> [P4] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions; fires; product spills; severe weather; geological events; global health crises, such as epidemics and pandemics; labor disputes; geopolitical tensions and escalations; armed hostilities; terrorist or piracy attacks; sabotage; civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater techn

> [P5] We are subject to income taxation in numerous jurisdictions worldwide. We record deferred tax assets and liabilities to account for the expected future tax consequences of events that have been recognized in our financial statements and our tax returns. We routinely assess our deferred tax assets and reduce such assets by a valuation allowance if we deem it is more likely than not that some portion, or all, of the deferred tax assets will not be realized. In assessing the need for adjustments to existing valuation allowances, we consider all available positive and negative evidence. Positive evidence includes reversals of temporary differences, forecasts of future taxable income, assessment

judge: supported

verdict: [ ]

## claim-023  (baseline text-086)

**Claim:** Financial impacts

> [P1] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P2] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P3] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions, fires, product spills, severe weather, geological events, global health crises, such as epidemics and pandemics, labor disputes, geopolitical tensions, armed hostilities, terrorist or piracy attacks, sabotage, civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater technological challen

> [P4] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions; fires; product spills; severe weather; geological events; global health crises, such as epidemics and pandemics; labor disputes; geopolitical tensions and escalations; armed hostilities; terrorist or piracy attacks; sabotage; civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater techn

> [P5] We are subject to income taxation in numerous jurisdictions worldwide. We record deferred tax assets and liabilities to account for the expected future tax consequences of events that have been recognized in our financial statements and our tax returns. We routinely assess our deferred tax assets and reduce such assets by a valuation allowance if we deem it is more likely than not that some portion, or all, of the deferred tax assets will not be realized. In assessing the need for adjustments to existing valuation allowances, we consider all available positive and negative evidence. Positive evidence includes reversals of temporary differences, forecasts of future taxable income, assessment

judge: supported

verdict: [ ]

## claim-024  (baseline text-073)

**Claim:** The approval for advanced clear cell RCC was based on the LITESPARK-005 trial

> [P1] Sales of Welireg, for the treatment of adult patients with certain VHL disease-associated tumors and certain adult patients with previously treated advanced RCC, more than doubled in 2024 primarily due to higher demand in the U.S. reflecting in part continued uptake of the RCC indication following approval by the FDA in December 2023. In November 2024, Welireg was approved in China for the treatment of adult patients with certain VHL disease-associated tumors not requiring immediate surgery based on the LITESPARK-004 clinical trial. In February 2025, the EC conditionally approved Welireg as monotherapy both for the treatment of adult patients with VHL disease who require therapy for associat

> [P2] February 2025 EC conditional approval as monotherapy for the treatment of adult patients with VHL disease who require therapy for associated, localized RCC, central nervous system hemangioblastomas, or pancreatic neuroendocrine tumors, and for whom localized procedures are unsuitable, based on the LITESPARK-004 trial. February 2025 EC conditional approval for the treatment of adult patients with advanced clear cell RCC that progressed following two or more lines of therapy that included a PD-1 or PD-L1 inhibitor and at least two vascular endothelial growth factor targeted therapies, based on the LITESPARK-005 trial. May 2025 FDA approval for the treatment of adult and pediatric patients (12

> [P3] Lynparza(2) January 2025 China’s NMPA approval for the adjuvant treatment of adult patients with deleterious or suspected deleterious germline BRCA-mutated, HER2-negative high-risk early breast cancer who have been previously treated with neoadjuvant or adjuvant chemotherapy, based on the OlympiA trial. Welireg February 2025 EC conditional approval as monotherapy for the treatment of adult patients with VHL disease who require therapy for associated, localized RCC, central nervous system hemangioblastomas, or pancreatic neuroendocrine tumors, and for whom localized procedures are unsuitable, based on the LITESPARK-004 trial. February 2025 EC conditional approval for the treatment of adult pa

> [P4] Lynparza(1) January 2025 China’s NMPA approval for the adjuvant treatment of adult patients with deleterious or suspected deleterious germline BRCA-mutated, HER2-negative high-risk early breast cancer who have been previously treated with neoadjuvant or adjuvant chemotherapy, based on the OlympiA trial. Table of Contents Welireg November 2024 China’s NMPA approval for the treatment of adult patients with VHL disease who require therapy for associated RCC, central nervous system hemangioblastomas or pancreatic neuroendocrine tumors. February 2025 EC conditional approval as monotherapy both for the treatment of adult patients with VHL disease who require therapy for associated, localized RCC,

> [P5] MK-6482, Welireg, is under review in Japan both for the treatment of adults with VHL disease based on the LITESPARK-004 clinical trial and for the treatment of certain adults with previously treated advanced RCC based on the LITESPARK-005 clinical trial. Additionally, in January 2025, the FDA accepted for priority review a supplemental NDA seeking approval of Welireg for the treatment of adult and pediatric patients (12 years and older) with advanced, unresectable, or metastatic pheochromocytoma and paraganglioma, based on the LITESPARK-015 trial. The FDA set a PDUFA, or target action, date of May 26, 2025. V116, Capvaxive, a 21-valent pneumococcal conjugate vaccine designed to help prevent

judge: supported

verdict: [ ]

## claim-025  (agent cross-193)

**Claim:** Microsoft's fiscal 2026 revenue was $331.839 billion

> [P1] Revenue increased $19.2 billion or 16%. •Microsoft 365 Commercial products and cloud services revenue increased $14.2 billion or 16%. Microsoft 365 Commercial cloud revenue grew 17% with growth in revenue per user driven by Microsoft 365 Copilot and Microsoft 365 E5. Microsoft 365 Commercial seats grew 6% driven by small and medium businesses and frontline worker offerings. Microsoft 365 Commercial products revenue grew 13% driven by growth in the Windows Commercial on-premises components of Microsoft 365 suite sales, as well as an increase in Office 2024 transactional purchasing. •Microsoft 365 Consumer products and cloud services revenue increased $1.8 billion or 24%. Microsoft 365 Consume

> [P2] Microsoft is a technology company committed to making digital technology and artificial intelligence (“AI”) available broadly and doing so responsibly, with a mission to empower every person and every organization on the planet to achieve more. We create platforms and applications, powered by AI, that deliver innovative solutions that meet the evolving needs of our customers. We generate revenue by offering a wide range of cloud-based solutions, content, and other services to people and businesses; licensing and supporting an array of software products; delivering relevant online advertising to a global audience; and designing and selling devices. Our most significant expenses are related to

> [P3] 2026 2025 Percentage Change Revenue $ 331,839 $ 281,724 18% Gross margin 225,465 193,893 16% Operating income 155,237 128,528 21% Net income 133,749 101,832 31% Diluted earnings per share 17.95 13.64 32% Adjusted net income (non-GAAP) 128,786 105,452 22% Adjusted diluted earnings per share (non-GAAP) 17.28 14.13 22% Adjusted net income and adjusted diluted earnings per share (“EPS”) are non-GAAP financial measures. These non-GAAP financial measures exclude net gains and losses from investments in OpenAI. Refer to the Non-GAAP Financial Measures section below for a reconciliation of our financial results reported in accordance with GAAP to non-GAAP financial results. Fiscal Year 2026 Compared

> [P4] •NIKE Brand wholesale revenues were $27.5 billion in fiscal 2026 compared to $25.9 billion in fiscal 2025, up 6% on a reported basis and up 4% on a currency-neutral basis. The increase on a currency-neutral basis was driven by higher revenues in North America, primarily offset by lower revenues in Greater China. •NIKE Direct revenues were $17.7 billion in fiscal 2026 compared to $18.8 billion in fiscal 2025, down 6% on a reported basis. On a currency-neutral basis, NIKE Direct revenues were down 8% due to declines in NIKE Brand Digital sales of 12% and declines in NIKE store sales of 4%. NIKE Brand Digital sales were $8.6 billion in fiscal 2026 compared to $9.6 billion in fiscal 2025, with d

> [P5] Seasonality Our revenue fluctuates quarterly and is generally higher in the fourth quarter of our fiscal year. Fourth quarter revenue is driven by a higher volume of multi-year contracts executed during the period. Reportable Segments We report our financial performance based on the following three segments: Productivity and Business Processes, Intelligent Cloud, and More Personal Computing. The segment amounts included in MD&A are presented on a basis consistent with our internal management reporting. Additional information on our reportable segments is contained in Note 18 – Segment Information and Geographic Data of the Notes to Financial Statements (Part II, Item 8 of this Form 10-K). Me

> [P6] More Personal Computing Revenue $ 54,052 $ 54,649 (1)% Cost of revenue 23,481 25,238 (7)% Operating expenses 16,185 15,245 6% Operating income $ 14,386 $ 14,166 2% Total Revenue $ 331,839 $ 281,724 18% Cost of revenue 106,374 87,831 21% Operating expenses 70,228 65,365 7% Operating income $ 155,237 $ 128,528 21% Reportable Segments Fiscal Year 2026 Compared with Fiscal Year 2025 Productivity and Business Processes

> [F1] ticker = MSFT, fiscal_year = 2025, metric = revenue, value = 281724000000.0

> [F2] ticker = MSFT, fiscal_year = 2026, metric = revenue, value = 331839000000.0

judge: supported

verdict: [ ]

## claim-026  (baseline text-148)

**Claim:** Revenue growth was driven by growth in Medicaid rates

> [P1] South American businesses held for sale 1,160 1,330 5,540 (170) (13) % UnitedHealthcare’s revenues increased due to the IRA-driven impacts on Medicare Part D plans and growth in the number of people served through Medicare Advantage, fee-based commercial offerings, those with higher acuity needs and Medicaid rates, partially offset by a decrease in people served through risk-based commercial offerings and Medicaid offerings. Earnings from operations decreased primarily due to the impacts of Medicare Advantage funding reductions, elevated medical cost trend, gains related to business portfolio refinement in 2024, the impacts of market morbidity changes on our individual exchange offerings, ot

> [P2] SELECTED OPERATING PERFORMANCE ITEMS The following summarizes select 2025 year-over-year operating comparisons to 2024 and other financial results. •Consolidated revenues grew 12%, UnitedHealthcare revenues grew 16% and Optum revenues grew 7%. •UnitedHealthcare served 415,000 more people domestically, driven by growth in fee-based commercial offerings and Medicare Advantage, partially offset by risk-based commercial offerings. •Earnings from operations of $19.0 billion compared to $32.3 billion last year, impacted by elevated medical cost trend, restructuring and other actions, gains related to business portfolio refinement in 2024, partially offset by net portfolio divestitures in 2025 and

> [P3] Worldwide sales were $65.0 billion in 2025, representing growth of 1% compared with 2024, or 2% excluding the unfavorable effect of foreign exchange. Global sales growth was primarily due to higher sales in the oncology franchise, largely due to the performance of Keytruda and Welireg, as well as increased alliance revenue from Koselugo (resulting from an amendment to the collaboration agreement), Reblozyl, and Lynparza. Also contributing to revenue growth in 2025 were higher sales in the cardiometabolic and respiratory franchise, largely attributable to the ongoing launch of Winrevair, as well as the inclusion of Ohtuvayre sales following the October 2025 acquisition of Verona Pharma. Growt

> [P4] For the Years Ended December 31, Change (in millions, except percentages) 2025 2024 2023 2025 vs. 2024 Revenues UnitedHealthcare $ 344,903 $ 298,208 $ 281,360 $ 46,695 16 % Optum Health 101,957 105,358 95,319 (3,401) (3) Optum Insight 19,417 18,757 18,932 660 4 Optum Rx 154,726 133,231 116,087 21,495 16 Optum eliminations (5,480) (4,389) (3,703) (1,091) 25 Optum 270,620 252,957 226,635 17,663 7 Eliminations (167,956) (150,887) (136,373) (17,069) 11 Consolidated revenues $ 447,567 $ 400,278 $ 371,622 $ 47,289 12 % Earnings from operations UnitedHealthcare $ 9,425 $ 15,584 $ 16,415 $ (6,159) (40) % Optum Health (278) 7,770 6,560 (8,048) (104) Optum Insight 2,624 3,097 4,268 (473) (15) Optum Rx

> [P5] Direct Response Costs – Cyberattack To support care providers impacted by the Change Healthcare cyberattack that occurred on February 21, 2024, the Company provided interest-free loans. In the fourth quarter of 2025, the Company increased its reserves for net collection expectations associated with provider loans and other customer balances of $799 million, which were recorded within operating costs on the Consolidated Statements of Operations and related to Optum Insight. Business Trends Our businesses participate primarily in the United States health markets. In the United States, health care spending has grown consistently for many years and accounted for 19% of gross domestic product (GD

judge: supported

verdict: [ ]

## claim-027  (baseline sql-062)

**Claim:** Johnson & Johnson's cash and cash equivalents were $24.1 billion at the end of fiscal year 2024

> [P1] Provision for Taxes on Income: The worldwide effective income tax rate from continuing operations was 15.7% in 2024 and 11.5% in 2023. For discussion related to the fiscal year 2024 provision for taxes refer to Note 8 to the Consolidated Financial Statements. On December 15, 2022, the European Union (EU) Member States formally adopted the EU’s Pillar Two Directive, which generally provides for a minimum effective tax rate of 15%, as established by the Organization for Economic Co-operation and Development (OECD) Pillar Two Framework that was supported by over 130 countries worldwide. Several EU and non-EU countries have enacted Pillar Two legislation with an initial effective date of January

> [P2] Interest (Income) Expense: Interest income in the fiscal years 2024 and 2023 was $1.3 billion. Interest expense in the fiscal years 2024 and 2023 was $0.8 billion. Cash, cash equivalents and marketable securities totaled $24.5 billion at the end of 2024, and averaged $23.7 billion as compared to the cash, cash equivalents and marketable securities total of $22.9 billion and $22.6 billion average balance in 2023. The total debt balance at the end of 2024 was $36.6 billion with an average debt balance of $33.0 billion as compared to $29.3 billion at the end of 2023 and an average debt balance of $34.5 billion. The higher debt balance was due to the senior unsecured notes issued by the Company

> [P3] Provision for Taxes on Income: The worldwide effective income tax rate from continuing operations was 17.7% in 2025 and 15.7% in 2024. For discussion related to the fiscal year 2025 provision for taxes refer to Note 8 to the Consolidated Financial Statements. On December 15, 2022, the European Union (EU) Member States formally adopted the EU’s Pillar Two Directive, which generally provides for a minimum effective tax rate of 15%, as established by the Organization for Economic Co-operation and Development (OECD) Pillar Two Framework that was supported by over 130 countries worldwide. Several EU and non-EU countries have enacted Pillar Two legislation with an initial effective date of January

> [P4] As of December 29, 2024, the Company's notes payable and long-term debt was in excess of cash, cash equivalents and marketable securities. As of December 29, 2024, the net debt position was $12.1 billion as compared to the prior year of $6.4 billion. The debt balance at the end of 2024 was $36.6 billion as compared to $29.3 billion in 2023. In the fiscal second quarter of 2024, the Company issued senior unsecured notes for a total of $6.7 billion. For additional details on borrowings, see Note 7 to the Consolidated Financial Statements. The net proceeds from this offering were used to fund the Shockwave acquisition which closed on May 31, 2024, and for general corporate purposes. Considering

> [P5] Interest (Income) Expense: Interest income in the fiscal year 2025 was $1.1 billion as compared to $1.3 billion in 2024. Interest income decreased as compared to the prior year driven by lower interest rates earned on cash balances. Interest expense in the fiscal year 2025 was $1.0 billion as compared to $0.8 billion in 2024. Interest expense was higher as compared to the prior year due to a higher average debt balance. Cash, cash equivalents and marketable securities totaled $20.1 billion at the end of 2025, and averaged $22.3 billion as compared to the cash, cash equivalents and marketable securities total of $24.5 billion and $23.7 billion average balance in 2024. The total debt balance a

judge: supported

verdict: [ ]

## claim-028  (agent text-096)

**Claim:** Alphabet files patent applications in the U.S. and foreign countries to cover certain of its technology

> [P1] For additional information about government regulation applicable to our business, see Item 1A Risk Factors; Trends in Our Business and Financial Effect in Part II, Item 7; and Legal Matters in Note 10 of the Notes to Consolidated Financial Statements included in Part II, Item 8 of this Annual Report on Form 10-K. 7. Table of Contents Alphabet Inc. Intellectual Property We rely on intellectual property such as trademarks, copyrights, patents, and trade secrets, as well as confidentiality procedures and contractual provisions, to protect our proprietary technology and our brand. We have registered, and applied for the registration of, US and international trademarks, service marks, domain nam

> [P2] We rely on various intellectual property laws, confidentiality procedures and contractual provisions to protect our proprietary technology and our brand. We have registered, and applied for the registration of, U.S. and international trademarks, service marks, domain names, and copyrights. We have also filed patent applications in the U.S. and foreign countries covering certain of our technology, and acquired patent assets to supplement our portfolio. We have licensed in the past, and expect that we may license in the future, certain of our rights to other parties. For additional information, see Item 1A Risk Factors of this Annual Report on Form 10-K. Available Information Our website is lo

> [P3] Our patents, trademarks, trade secrets, copyrights, and other intellectual property rights are important assets for us. Various events outside of our control pose a threat to our intellectual property rights, as well as to our products, services, and technologies. For example, effective intellectual property protection may not be available in every country in which our products and services are distributed or made available through the Internet. Also, the efforts we have taken and may take in the future to protect our proprietary rights, including obtaining copyright and patent protections for our important innovations, including AI innovations, may not be sufficient or effective. There is a

> [P4] for many aspects of our business, including higher level of investment in technical infrastructure. Further, certain of our costs and expenses are generally less variable in nature and may not correlate to changes in revenue. We may also not be able to continue to execute our efficiency efforts successfully or in a timely manner. Due to these factors and the evolving nature of our business, our historical revenue growth rate and historical operating margin may not be indicative of our future performance. For additional information, see Trends in Our Business and Financial Effect and Revenues and Monetization Metrics in Part II, Item 7 of this Annual Report on Form 10-K. Our intellectual prop

> [P5] 17. Table of Contents Alphabet Inc. •Data privacy, collection, processing, and portability: Laws and regulations further restricting the collection, processing, or sharing of user or advertising-related data, including privacy and data protection laws; laws affecting the processing of children's data (as discussed further below), data breach notification laws; laws limiting data transfers (including data localization laws); laws limiting use of data for AI training; and laws requiring data portability. •Copyright and other intellectual property: Copyright and related laws, including the EU Directive on Copyright in the Digital Single Market and European Economic Area transpositions, which ha

> [P6] Intellectual Property. We regard our trademarks, service marks, copyrights, patents, domain names, trade dress, trade secrets, proprietary technologies and similar intellectual property as important to our success, and with respect to our associates, customers and others, we rely on trademark, copyright, and patent laws, trade-secret protection, and confidentiality and/or license agreements to protect our proprietary rights. We have registered, or applied for the registration of, a number of U.S. and international domain names, trademarks, service marks and copyrights. Additionally, we have filed U.S. and international patent applications covering certain of our proprietary technology. We ha

judge: supported

verdict: [ ]

## claim-029  (baseline cross-181)

**Claim:** The increase in free cash flow to $6.1 billion in fiscal 2024 was primarily due to higher net income and lower income tax payments, partially offset by a decrease in All other operating activities and working capital growth, after adjusting for an increase in Corporate & Other restructuring cash expenditures.

> [P1] Cash used for financing activities was $10.5 billion in 2023, a decrease of $3.0 billion compared with 2022, primarily due to: cash paid to repurchase long-term debt of $6.9 billion, including debt extinguishment costs in 2022, lower other net debt maturities of $0.5 billion, lower cash paid on derivatives hedging foreign currency debt of $0.7 billion, an increase in cash received of $0.5 billion from stock option exercises, the settlement of Concept Laser GmbH's interest of $0.2 billion in 2022 (components of All other financing activities); partially offset by higher cash paid for redemption of GE preferred stock of $5.7 billion. Free cash flow* (FCF) was $6.1 billion and $4.7 billion for

> [P2] CASH FLOWS FROM CONTINUING OPERATIONS. The most significant source of cash flows from operating activities (CFOA) is customer-related activities, the largest of which is collecting cash resulting from equipment or services sales. The most significant operating use of cash is to pay our suppliers, employees, tax authorities and postretirement plans. GE Aerospace measures itself on a free cash flow* basis. This metric includes CFOA plus investments in property, plant and equipment and additions to internal-use software, and this metric excludes any cash received from dispositions of property, plant and equipment. Cash from operating activities was $5.8 billion in 2024, an increase of $1.2 bill

> [P3] CASH FLOWS FROM CONTINUING OPERATIONS. The most significant source of cash flows from operating activities (CFOA) is customer-related activities, the largest of which is collecting cash resulting from equipment or services sales. The most significant operating use of cash is to pay our suppliers, employees, tax authorities and postretirement plans. GE Aerospace measures itself on a free cash flow* basis. This metric includes CFOA plus investments in property, plant and equipment and internal-use software and cash received from dispositions of property, plant and equipment. Cash from operating activities was $8.5 billion in 2025, an increase of $2.7 billion compared to 2024, primarily due to:

> [P4] Additionally, the DoD is focused on advanced combat, enhancing platform capability and groundbreaking technology primarily in classified programs, including support for the next generation T901 turboshaft engine and advanced engine architectures. In June 2024, GE Aerospace delivered two T901-GE-900 engines to Sikorsky for integration and testing aboard a UH-60 Black Hawk as part of the U.S. Army upgrade program. In addition, GE Aerospace was awarded a $1.1 billion contract to provide T700 series turbine engines to the U.S. Army through the first half of 2029. Sales in units, except where noted 2024 2023 2022 Defense engines 490 556 632 SEGMENT REVENUE AND PROFIT 2024 2023 2022 Defense & Syst

> [P5] Cash from investing activities was $7.7 billion in 2023, a decrease of $2.7 billion compared with 2022, primarily due to: higher cash paid related to net settlements between our continuing operations and businesses in discontinued operations of $6.3 billion, primarily related to lower cash received of $7.6 billion related to the separation of GE Healthcare partially offset by higher cash received of $0.8 billion from the separation of GE Vernova and an increase in cash paid for derivatives settlements of $0.4 billion (components of All other investing activities); partially offset by an increase in proceeds of $4.3 billion from the disposition of our retained ownership interests in GE Health

judge: supported

verdict: [ ]

## claim-030  (agent text-088)

**Claim:** Keytruda is approved as a monotherapy for urothelial cancer, including non-muscle invasive bladder cancer.

> [P1] Pharmaceutical The Pharmaceutical segment includes human health pharmaceutical and vaccine products. Human health pharmaceutical products consist of therapeutic and preventive agents, generally sold by prescription, for the treatment of human disorders. Human health vaccine products consist of preventive pediatric, adolescent and adult vaccines. Certain of the products within the Company’s franchises are as follows: Table of Contents Oncology Keytruda is an anti-PD-1 (programmed death receptor-1) therapy that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroeso

> [P2] The Company received more than 25 regulatory approvals in major markets in 2024, including the Winrevair and Capvaxive approvals noted above, along with numerous approvals in oncology. Keytruda received approval for additional indications in the U.S. and/or internationally as monotherapy in the therapeutic areas of hepatocellular carcinoma (HCC), melanoma and urothelial carcinoma, in combination with chemotherapy in the therapeutic areas of biliary tract cancer, cervical cancer, endometrial carcinoma, gastric or gastroesophageal junction (GEJ) adenocarcinoma, malignant pleural mesothelioma and non-small-cell lung cancer (NSCLC), as well as in combination with Padcev (enfortunab vedotin-ejfv)

> [P3] MK-3475, Keytruda, is an anti-PD-1 therapy approved for the treatment of many cancers that is in clinical development for expanded indications. These studies encompass more than 30 cancer types including: biliary, estrogen receptor positive breast, triple-negative breast, cervical, colorectal, endometrial, esophageal, gastric, glioblastoma, head and neck, hepatocellular, Hodgkin lymphoma, non-Hodgkin lymphoma, non-small-cell lung, small-cell lung, melanoma, malignant pleural mesothelioma, ovarian, prostate, renal, and urothelial, several of which are currently in Phase 3 clinical development. Further trials are being planned for other cancers. Keytruda is under review in the EU and Japan for

> [P4] Keytruda (pembrolizumab) is an anti-PD-1 (programmed death receptor-1) therapy available for intravenous administration that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroesophageal junction (GEJ) carcinoma, head and neck squamous cell carcinoma (HNSCC), hepatocellular carcinoma (HCC), melanoma, Merkel cell carcinoma, microsatellite instability-high (MSI-H) or mismatch repair deficient (dMMR) solid tumors (including MSI-H/dMMR colorectal cancer and endometrial carcinoma), non-small cell lung cancer (NSCLC), primary mediastinal large B-cell lymphoma (PMBCL),

> [P5] Disease (JPN) Pneumococcal Vaccine Adult V116 Capvaxive (EU) (JPN) Pulmonary Arterial Hypertension MK-7962 Winrevair (JPN) Respiratory Syncytial Virus MK-1654 (clesrovimab) (U.S.) (EU) Certain Supplemental Filings Cancer MK-3475 Keytruda • First-Line Unresectable Advanced or Metastatic Malignant Pleural Mesothelioma (KEYNOTE-483) (EU) (JPN) MK-6482 Welireg • Advanced, Unresectable, or Metastatic Pheochromocytoma and Paraganglioma (LITESPARK-015) (U.S.) Footnotes: (1) Being developed in a collaboration. (2) Being developed in combination with Keytruda. (3) Being developed as monotherapy and/or in combination with Keytruda. (4) FDA lifted clinical hold on December 4, 2024. (5) On FDA partial c

> [P6] Keytruda is an anti-PD-1 therapy that has been approved in over 40 indications in the U.S., including 18 tumor types and 2 tumor-agnostic indications, and has similarly been approved in markets worldwide for many of these indications. The Keytruda clinical development program includes studies across a broad range of cancer types. Global sales of Keytruda grew 18% in 2024, or 22% excluding the unfavorable effect of foreign exchange. The negative impact of foreign exchange was primarily due to the devaluation of the Argentine peso, which was largely offset by inflation-related price increases consistent with practice in that market. Keytruda sales growth in the U.S. reflects higher demand acro

judge: supported

verdict: [ ]

## claim-031  (baseline text-132)

**Claim:** Apple identifies marketing and distribution capability as a principal competitive factor important to its success

> [P1] The markets for the Company’s products and services are highly competitive and are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. The markets in which the Company competes are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements by competitors. Many of the Company’s competitors seek to compete primarily through aggressive pricing and very low cost structures, and by imitating the Company’s products and infringing on its intellec

> [P2] The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs and develops nearly the entire solution for its products, including the hardware, operating system, numerous software applications and related services. Principal competitive factors important to the Company include price, product and service features (including security features), relative price and performance, product and service quality and reliability, design innovation, a strong third-party software and accessories ecosystem, marketing and distribution capability, service and suppor

> [P3] The Company’s products and services are offered in highly competitive global markets. These markets are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. These markets are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements. The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs an

> [P4] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number of factors, including timely and successful development, market accepta

> [P5] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, navigate global regulatory requirements and barriers to market access, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number

judge: supported

verdict: [ ]

## claim-032  (agent text-144)

**Claim:** Nvidia has invested $72.11 billion in research and development since its inception

> [F1] ticker = NVDA, cumulative_rd_expense = 72107276000.0

judge: supported

verdict: [ ]

## claim-033  (baseline text-146)

**Claim:** If Nvidia is unable to comply with regulations in jurisdictions such as the European Union, it may impede the company's ability to offer certain products and services in those jurisdictions.

> [P1] If we enable or offer solutions that draw controversy due to their perceived or actual impact on society, such as AI solutions that have unintended consequences, infringe copyright or rights of publicity, or are controversial because of their impact on human rights, privacy, employment or other social, economic or political issues, or if we are unable to develop effective internal policies and frameworks relating to the responsible development and use of AI models and systems offered through our sales channels, we may experience brand or reputational harm, competitive harm or legal liability. Leveraging AI capabilities to potentially improve our internal functions and operations may present

> [P2] Compliance with laws, rules, and regulations has not otherwise had a material effect upon our capital expenditures, results of operations, or competitive position and we do not currently anticipate material capital expenditures for environmental control facilities. Compliance with existing or future governmental regulations, including, but not limited to, those pertaining to IP ownership and infringement, taxes, import and export requirements and tariffs, anti-corruption, business acquisitions, foreign exchange controls and cash repatriation restrictions, data privacy requirements, competition and antitrust, advertising, employment, product regulations, cybersecurity, environmental, health a

> [P3] On January 15, 2025, the USG published the “AI Diffusion” IFR in the Federal Register. After a 120-day delayed compliance period, the IFR will, unless modified, impose a worldwide licensing requirement on all products classified under Export Control Classification Numbers, or ECCNs, 3A090.a, 4A090.a, or corresponding .z ECCNs, including all related software and technology. Any system that incorporates one or more of the covered integrated circuits, or ICs, (including but not limited to NVIDIA DGX, HGX, and MGX systems) will be covered by the new licensing requirement. The licensing requirement will include future NVIDIA ICs, boards, or systems classified with ECCN 3A090.a or 4A090.a, or corr

> [P4] Governments and regulators are also considering, and in certain cases, have imposed restrictions on the hardware, software, and systems used to develop frontier foundation models and generative AI. For example, the EU AI Act became effective on August 1, 2024 and will be fully applicable after a two-year transitional period. The EU AI Act may impact our ability to train, deploy, or release AI models in the EU. Several states are considering enacting or have already enacted regulations concerning AI technologies, which may impact our ability to train, deploy, or release AI models, and increase our compliance costs. Restrictions under these and any other regulations, if implemented, could incr

> [P5] Certain shareholder advocacy groups, investment funds, shareholders and other market participants, customers and government regulators have focused on corporate sustainability practices and disclosures, including those associated with climate change and human rights. Stakeholders may not be satisfied with our corporate sustainability practices and goals or the speed of their adoption. Further, there are state-level initiatives in the U.S. that may differ from other regulatory requirements or our various stakeholders’ expectations. Additionally, our corporate sustainability practices, oversight of our practices or disclosure controls may not meet evolving shareholder, regulator or other indus

judge: supported

verdict: [ ]

## claim-034  (baseline cross-167)

**Claim:** For Amazon's fiscal year 2024, the total consolidated net sales were $637,959 million

> [P1] Table of Contents AWS sales increased 19% in 2024, compared to the prior year. The sales growth primarily reflects increased customer usage, partially offset by pricing changes primarily driven by long-term customer contracts. Operating Expenses Information about operating expenses is as follows (in millions): Year Ended December 31, 2023 2024 Operating Expenses: Cost of sales $ 304,739 $ 326,288 Fulfillment 90,619 98,505 Technology and infrastructure 85,622 88,544 Sales and marketing 44,370 43,907 General and administrative 11,816 11,359 Other operating expense (income), net 767 763 Total operating expenses $ 537,933 $ 569,366 Year-over-year Percentage Growth (Decline): Cost of sales 6 % 7

> [P2] Table of Contents by our continued focus on price, selection, and convenience for our customers, including from our fast shipping offers. Changes in foreign exchange rates increased International net sales by $4.9 billion in 2025. AWS sales increased 20% in 2025, compared to the prior year. The sales growth primarily reflects increased customer usage, partially offset by pricing changes primarily driven by long-term customer contracts. Operating Expenses Information about operating expenses is as follows (in millions): Year Ended December 31, 2024 2025 Operating Expenses: Cost of sales $ 326,288 $ 356,414 Fulfillment 98,505 109,074 Technology and infrastructure 88,544 108,521 Sales and marke

> [P3] Operating Income (Loss) North America $ 14,877 $ 24,967 International (2,656) 3,792 AWS 24,631 39,834 Consolidated $ 36,852 $ 68,593 Operating income was $36.9 billion and $68.6 billion for 2023 and 2024. We believe that operating income is a more meaningful measure than gross profit and gross margin due to the diversity of our product categories and services. For more information on the operating expenses that impact segment operating income, see “Operating Expenses” and the descriptions of operating expense line item changes on pages 25 to 27, and “Note 10 — Segment Information” on page 65. The increase in North America operating income in 2024, compared to the prior year, is primarily due

> [P4] Year Ended December 31, 2023 2024 Net Sales: North America $ 352,828 $ 387,497 International 131,200 142,906 AWS 90,757 107,556 Consolidated $ 574,785 $ 637,959 Year-over-year Percentage Growth: North America 12 % 10 % International 11 9 AWS 13 19 Consolidated 12 11 Year-over-year Percentage Growth, excluding the effect of foreign exchange rates: North America 12 % 10 % International 11 10 AWS 13 19 Consolidated 12 11 Net Sales Mix: North America 61 % 61 % International 23 22 AWS 16 17

> [P5] Year Ended December 31, 2024 2025 Operating Income North America $ 24,967 $ 29,619 International 3,792 4,750 AWS 39,834 45,606 Consolidated $ 68,593 $ 79,975 Operating income was $68.6 billion and $80.0 billion for 2024 and 2025. Operating income for 2025 includes charges of $2.5 billion we recorded in Q3 2025 related to the settlement of a lawsuit with the FTC and $2.7 billion, of which $1.8 billion was recorded in Q3 2025, of estimated severance costs primarily related to planned role eliminations. We believe that operating income is a more meaningful measure than gross profit and gross margin due to the diversity of our product categories and services. For more information on the operatin

judge: supported

verdict: [ ]

## claim-035  (agent text-131)

**Claim:** The company uses hedging and other risk management techniques to manage a portion of these exposures.

> [P1] As a global company, we face foreign currency risk exposure from fluctuating currency exchange rates, interest rate risk from our exposure to floating and variable interest rates, and existing and expected rates of inflation or deflation in the U.S. and other jurisdictions, each of which impacts our results of operations. We are a net receiver of most foreign currencies, and our results of operations are adversely impacted when the U.S. dollar is strong compared to foreign currencies. Rapid growth in our international business and changes in the global supply chain for our products have impacted and may continue to impact our foreign currency exposure. Further, in the event of an extreme dev

> [P2] These and similar events have adversely affected, and may continue to adversely affect, us, our business partners, and our customers. For more details, see Item 1, "Business—Regulations and Private Payer Actions Affecting Pharmaceutical Pricing, Reimbursement, and Access." In addition to developments related to our business or financial results, or those of our competitors, uneven economic growth, downturns, or other negative global developments, could also undermine our growth or result in significant and sudden declines in the trading price of our common stock and market capitalization. •Changes in foreign currency rates, interest rate risks, and inflation or deflation affect our results o

> [P3] Our foreign currency risk exposure results from fluctuating currency exchange rates, primarily the U.S. dollar against the euro, Japanese yen, and Chinese yuan. We face foreign currency exchange exposures when we enter into transactions arising from subsidiary trade and loan payables and receivables denominated in foreign currencies. We also face currency exposure that arises from translating the results of our global operations to the U.S. dollar at exchange rates that have fluctuated from the beginning of the period. We in some cases enter into foreign currency forward or option derivative contracts to reduce the effect of fluctuating currency exchange rates (primarily the euro, Chinese yu

> [P4] Our foreign currency risk exposure results from fluctuating currency exchange rates, primarily the U.S. dollar against the euro, Japanese yen, Chinese yuan, and British pound sterling. We face foreign currency exchange exposures when we enter into transactions arising from subsidiary trade and loan payables and receivables denominated in foreign currencies. We also face currency exposure that arises from translating the results of our global operations to the U.S. dollar at exchange rates that have fluctuated from the beginning of the period. We in some cases enter into foreign currency forward or option derivative contracts to reduce the effect of fluctuating currency exchange rates. Our co

> [P5] Continued regulatory focus on business combinations in our industry, including by the Federal Trade Commission and competition authorities in Europe and other jurisdictions, could continue to delay, jeopardize, or increase the costs of our business development activities and may negatively impact our consolidated financial position or results of operations. For discussion of risks related to business development activities, see Item 1A, "Risk Factors—Risks Related to Our Business and Industry—Pharmaceutical research and development is very costly and highly uncertain; we may not succeed in developing, licensing, or acquiring commercially successful products sufficient in number or value to r

> [P6] Foreign Currency Exchange Rates As a global company, we face foreign currency risk exposure from fluctuating currency exchange rates, primarily the U.S. dollar against the euro, Japanese yen, Chinese yuan, and British pound sterling. While we seek to manage a portion of these exposures through hedging and other risk management techniques, significant fluctuations in currency rates can have a material impact, either positive or negative, on our consolidated results of operations in any given period. There is uncertainty in the future movements in foreign currency exchange rates, and fluctuations in these rates have and could adversely impact our consolidated results of operations and cash flo

judge: supported

verdict: [ ]

## claim-036  (baseline adversarial-007)

**Claim:** If dealers do not maintain sufficient inventory, Caterpillar may lose time-sensitive sales

> [P1] In the first quarter of 2026 as compared to the first quarter of 2025, we expect stronger sales and revenues primarily due to higher sales volume and favorable price realization. We expect higher sales volume to be mainly driven by higher sales of equipment to end users and by the impact from changes in machine dealer inventories. We expect machine dealer inventory to increase in excess of $1.0 billion during the first quarter of 2026, aligning with the seasonal pattern, compared to roughly flat levels in the first quarter of 2025. In the first quarter of 2026 as compared to the first quarter of 2025, we anticipate strong sales growth in Construction Industries, primarily due to higher sales

> [P2] North America sales decreased 1 percent primarily due to lower sales volume, partially offset by favorable price realization. The decrease in sales volume was mainly due to the impact from changes in dealer inventories. Dealer inventory increased less during 2024 than during 2023. Sales increased 1 percent in Latin America. Unfavorable currency impacts related to the Brazilian real were more than offset by higher sales volume and favorable price realization. The increase in sales volume was primarily due to the impact from changes in dealer inventories. Dealer inventory increased during 2024, compared to a decrease during 2023. EAME sales decreased 10 percent primarily due lower sales volume

> [P3] We continue to monitor a variety of external factors around the world, such as supply chain disruptions, inflationary cost and labor pressures. Areas of particular focus include transportation, certain components and raw materials. We continue to work to minimize supply chain challenges that may impact our ability to meet customer demand. We continue to assess the environment to determine if additional actions need to be taken. Risk Factors Risk factors are disclosed within Item 1A. Risk Factors of the 2024 Form 10-K. Notes: •Glossary of terms included on pages 35 - 37; first occurrence of terms shown in bold italics. •Information on non-GAAP financial measures is included on pages 47 - 48.

> [P4] EAME sales increased 4 percent mainly due to higher sales volume and favorable currency impacts related to the euro, partially offset by unfavorable price realization. The increase in sales volume was primarily driven by the impact from changes in dealer inventories. Dealer inventory increased in 2025, compared to a decrease in 2024. Asia/Pacific sales decreased 2 percent primarily due to unfavorable currency impacts related to the Australian dollar, and lower sales volume. The decrease in sales volume was mainly driven by lower sales of equipment to end users. Total dealer inventory increased about $900 million during 2025, compared to an increase of about $400 million during 2024. Machine

> [P5] We sell finished products primarily through an independent dealer network and directly to OEMs and are subject to risks relating to their inventory management decisions and operational and sourcing practices. Both carry inventories of finished products as part of ongoing operations and adjust those inventories based on their assessments of future needs and market conditions, including levels of used equipment inventory and machine rental usage rates. Such adjustments may impact our results positively or negatively. If the inventory levels of our dealers and OEM customers are higher than they desire, they may postpone product purchases from us, which could cause our sales to be lower than the

judge: supported

verdict: [ ]

## claim-037  (baseline text-088)

**Claim:** Keytruda is approved as monotherapy for primary mediastinal large B-cell lymphoma (PMBCL)

> [P1] Pharmaceutical The Pharmaceutical segment includes human health pharmaceutical and vaccine products. Human health pharmaceutical products consist of therapeutic and preventive agents, generally sold by prescription, for the treatment of human disorders. Human health vaccine products consist of preventive pediatric, adolescent and adult vaccines. Certain of the products within the Company’s franchises are as follows: Table of Contents Oncology Keytruda is an anti-PD-1 (programmed death receptor-1) therapy that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroeso

> [P2] The Company received more than 25 regulatory approvals in major markets in 2024, including the Winrevair and Capvaxive approvals noted above, along with numerous approvals in oncology. Keytruda received approval for additional indications in the U.S. and/or internationally as monotherapy in the therapeutic areas of hepatocellular carcinoma (HCC), melanoma and urothelial carcinoma, in combination with chemotherapy in the therapeutic areas of biliary tract cancer, cervical cancer, endometrial carcinoma, gastric or gastroesophageal junction (GEJ) adenocarcinoma, malignant pleural mesothelioma and non-small-cell lung cancer (NSCLC), as well as in combination with Padcev (enfortunab vedotin-ejfv)

> [P3] MK-3475, Keytruda, is an anti-PD-1 therapy approved for the treatment of many cancers that is in clinical development for expanded indications. These studies encompass more than 30 cancer types including: biliary, estrogen receptor positive breast, triple-negative breast, cervical, colorectal, endometrial, esophageal, gastric, glioblastoma, head and neck, hepatocellular, Hodgkin lymphoma, non-Hodgkin lymphoma, non-small-cell lung, small-cell lung, melanoma, malignant pleural mesothelioma, ovarian, prostate, renal, and urothelial, several of which are currently in Phase 3 clinical development. Further trials are being planned for other cancers. Keytruda is under review in the EU and Japan for

> [P4] Keytruda (pembrolizumab) is an anti-PD-1 (programmed death receptor-1) therapy available for intravenous administration that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroesophageal junction (GEJ) carcinoma, head and neck squamous cell carcinoma (HNSCC), hepatocellular carcinoma (HCC), melanoma, Merkel cell carcinoma, microsatellite instability-high (MSI-H) or mismatch repair deficient (dMMR) solid tumors (including MSI-H/dMMR colorectal cancer and endometrial carcinoma), non-small cell lung cancer (NSCLC), primary mediastinal large B-cell lymphoma (PMBCL),

> [P5] Disease (JPN) Pneumococcal Vaccine Adult V116 Capvaxive (EU) (JPN) Pulmonary Arterial Hypertension MK-7962 Winrevair (JPN) Respiratory Syncytial Virus MK-1654 (clesrovimab) (U.S.) (EU) Certain Supplemental Filings Cancer MK-3475 Keytruda • First-Line Unresectable Advanced or Metastatic Malignant Pleural Mesothelioma (KEYNOTE-483) (EU) (JPN) MK-6482 Welireg • Advanced, Unresectable, or Metastatic Pheochromocytoma and Paraganglioma (LITESPARK-015) (U.S.) Footnotes: (1) Being developed in a collaboration. (2) Being developed in combination with Keytruda. (3) Being developed as monotherapy and/or in combination with Keytruda. (4) FDA lifted clinical hold on December 4, 2024. (5) On FDA partial c

judge: supported

verdict: [ ]

## claim-038  (agent text-092)

**Claim:** In assessing its insurance coverage, Eli Lilly considers the potential for denial of coverage by the insurance company.

> [P1] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P2] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P3] We are subject to a substantial number of claims, litigation, and investigations involving various current and historical products and practices. These claims relate to how we commercialize and/or how we price our products, product safety, our operations as well as contractual matters and other disputes. We have also filed lawsuits and taken other legal actions to protect our intellectual property and address unlawful practices. See Item 8, "Financial Statements and Supplementary Data—Note 16: Contingencies," for more information on certain matters. Like many companies in our industry, from time to time investigations into aspects of our business include inquiries, subpoenas, and other types

> [P4] initiated enforcement or other actions across industries to seek alignment with policy initiatives. Because of the nature of pharmaceutical products and our evolving business, we are, and could increasingly become, subject to large numbers of product liability claims for our previous, current, or future products, or to further litigation or investigations, including related to product safety, marketing, pricing, or other commercial practices. Some of these matters involve or may involve numerous plaintiffs and parties seeking large or indeterminate financial claims and may remain unresolved for several years. Such matters could negatively impact our reputation, affect our results of operatio

> [P5] We derive a significant percentage of our total revenue from relatively few products and sell our products through consolidated supply chain entities, which subjects us to various risks. We derived direct product and/or collaboration and other revenues of more than $3 billion for each of Mounjaro, Zepbound, Verzenio, Trulicity, Taltz, and Jardiance (including Glyxambi, Synjardy, and Trijardy XR) that collectively accounted for 82 percent of our total revenues in 2025. In particular, Mounjaro and Zepbound accounted for 56 percent of our total revenues in 2025, and we expect cardiometabolic health products will continue to represent a significant and growing portion of our business, revenues,

> [P6] Risks Related to Litigation and Government Regulation •We are party to litigation and investigations related to our products, how we price or commercialize our products, and other aspects of our business, which could adversely affect our business, and we are self-insured for such matters.

judge: supported

verdict: [ ]

## claim-039  (baseline text-157)

**Claim:** These laws and regulations are evolving and subject to interpretation; compliance obligations could cause Alphabet to incur substantial costs or harm the quality and operations of its products and services.

> [P1] Further, we are subject to evolving laws and regulations that dictate whether, how, and under what circumstances we can transfer, process, or receive personal data, as well as ongoing enforcement actions from supervisory authorities related to cross-border transfers of personal data. The validity of various data transfer mechanisms we currently rely upon remains subject to legal, regulatory, and political developments globally, which may require us to adapt our existing arrangements. We face, and may continue to face, intellectual property infringement or misappropriation, violation of rights of publicity, and other claims that could be costly to defend, result in significant damage awards o

> [P2] 21. Table of Contents Alphabet Inc. Further, we are subject to evolving laws and regulations that dictate whether, how, and under what circumstances we can transfer, process and/or receive personal data, as well as ongoing enforcement actions from supervisory authorities related to cross-border transfers of personal data. The validity of various data transfer mechanisms we currently rely upon remains subject to legal, regulatory, and political developments globally, which may require us to adapt our existing arrangements. We face, and may continue to face, intellectual property infringement or misappropriation, violation of rights of publicity, and other claims that could be costly to defend

> [P3] Our international operations expose us to additional risks that could harm our business, reputation, financial condition, and operating results. 14. Table of Contents Alphabet Inc. Our international operations are significant to our revenues and net income, and we plan to continue to grow internationally. International revenues accounted for approximately 51% of our consolidated revenues in 2024. In addition to risks described elsewhere in this section, our international operations expose us to other risks, including the following: •restrictions on foreign ownership and investments, and stringent foreign exchange controls that might prevent us from repatriating cash earned in countries outsi

> [P4] of data protection laws, imposing specific obligations with respect to the processing of personal data, including required notices, consents, and opt-outs. Further, the increased risk of inadvertent disclosure of confidential information or personal data in connection with the utilization of AI technologies may result in stronger regulatory scrutiny, leading to legal and regulatory investigations and enforcement actions that could harm our business, even if unfounded. Adverse legal rulings, legislation, or regulation have resulted in, and may continue to result in, fines and orders requiring that we change our practices, which have had and could continue to have an adverse effect on how we p

> [P5] Our operations and financial results are subject to various risks and uncertainties, including but not limited to those described below, which could harm our business, reputation, financial condition, and operating results, and affect the trading price of our Class A and Class C stock. Risks Specific to our Company We generate a significant portion of our revenues from advertising. Reduced spending by advertisers, a loss of partners, or new and existing technologies that block ads online and/or affect our ability to personalize ads could harm our business. We generated more than 75% of total revenues from online advertising in 2024. Many of our advertisers, companies that distribute our prod

judge: supported

verdict: [ ]

## claim-040  (agent sql-060)

**Claim:** UnitedHealth's capital expenditures for fiscal year 2025 were $3622000000.0

> [F1] ticker = UNH, fiscal_year = 2025, metric = capital_expenditures, value = 3622000000.0

judge: supported

verdict: [ ]

## claim-041  (baseline text-088)

**Claim:** Keytruda is approved as monotherapy for microsatellite instability-high (MSI-H) or mismatch repair deficient (dMMR) solid tumors (including MSI-H/dMMR colorectal cancer and endometrial carcinoma)

> [P1] Pharmaceutical The Pharmaceutical segment includes human health pharmaceutical and vaccine products. Human health pharmaceutical products consist of therapeutic and preventive agents, generally sold by prescription, for the treatment of human disorders. Human health vaccine products consist of preventive pediatric, adolescent and adult vaccines. Certain of the products within the Company’s franchises are as follows: Table of Contents Oncology Keytruda is an anti-PD-1 (programmed death receptor-1) therapy that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroeso

> [P2] The Company received more than 25 regulatory approvals in major markets in 2024, including the Winrevair and Capvaxive approvals noted above, along with numerous approvals in oncology. Keytruda received approval for additional indications in the U.S. and/or internationally as monotherapy in the therapeutic areas of hepatocellular carcinoma (HCC), melanoma and urothelial carcinoma, in combination with chemotherapy in the therapeutic areas of biliary tract cancer, cervical cancer, endometrial carcinoma, gastric or gastroesophageal junction (GEJ) adenocarcinoma, malignant pleural mesothelioma and non-small-cell lung cancer (NSCLC), as well as in combination with Padcev (enfortunab vedotin-ejfv)

> [P3] MK-3475, Keytruda, is an anti-PD-1 therapy approved for the treatment of many cancers that is in clinical development for expanded indications. These studies encompass more than 30 cancer types including: biliary, estrogen receptor positive breast, triple-negative breast, cervical, colorectal, endometrial, esophageal, gastric, glioblastoma, head and neck, hepatocellular, Hodgkin lymphoma, non-Hodgkin lymphoma, non-small-cell lung, small-cell lung, melanoma, malignant pleural mesothelioma, ovarian, prostate, renal, and urothelial, several of which are currently in Phase 3 clinical development. Further trials are being planned for other cancers. Keytruda is under review in the EU and Japan for

> [P4] Keytruda (pembrolizumab) is an anti-PD-1 (programmed death receptor-1) therapy available for intravenous administration that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroesophageal junction (GEJ) carcinoma, head and neck squamous cell carcinoma (HNSCC), hepatocellular carcinoma (HCC), melanoma, Merkel cell carcinoma, microsatellite instability-high (MSI-H) or mismatch repair deficient (dMMR) solid tumors (including MSI-H/dMMR colorectal cancer and endometrial carcinoma), non-small cell lung cancer (NSCLC), primary mediastinal large B-cell lymphoma (PMBCL),

> [P5] Disease (JPN) Pneumococcal Vaccine Adult V116 Capvaxive (EU) (JPN) Pulmonary Arterial Hypertension MK-7962 Winrevair (JPN) Respiratory Syncytial Virus MK-1654 (clesrovimab) (U.S.) (EU) Certain Supplemental Filings Cancer MK-3475 Keytruda • First-Line Unresectable Advanced or Metastatic Malignant Pleural Mesothelioma (KEYNOTE-483) (EU) (JPN) MK-6482 Welireg • Advanced, Unresectable, or Metastatic Pheochromocytoma and Paraganglioma (LITESPARK-015) (U.S.) Footnotes: (1) Being developed in a collaboration. (2) Being developed in combination with Keytruda. (3) Being developed as monotherapy and/or in combination with Keytruda. (4) FDA lifted clinical hold on December 4, 2024. (5) On FDA partial c

judge: supported

verdict: [ ]

## claim-042  (baseline text-153)

**Claim:** Physical commodities activities are subject to extensive federal, state, and local energy, environmental, and antitrust regulations

> [P1] THE GOLDMAN SACHS GROUP, INC. AND SUBSIDIARIES Legal and Regulatory Our businesses and those of our clients are subject to extensive and pervasive regulation around the world. As a participant in the financial services industry and a globally systemically important financial institution, we are subject to extensive regulation in jurisdictions around the world. We face the risk of significant intervention by law enforcement, regulatory and taxing authorities, as well as private litigation, in all jurisdictions in which we conduct our businesses. In many cases, our activities have been and may continue to be subject to overlapping and divergent regulation in different jurisdictions. Among othe

> [P2] Goldman Sachs 2024 Form 10-K THE GOLDMAN SACHS GROUP, INC. AND SUBSIDIARIES As a result of our recovery and resolution planning processes, including incorporating feedback from our regulators, we may incur increased operational, funding or other costs and face limitations on our ability to structure our internal organization or engage in internal or external activities in a manner that we may otherwise deem most operationally efficient. Our commodities activities, particularly our physical commodities activities, subject us to extensive regulation and involve certain potential risks, including environmental, reputational and other risks that may expose us to significant liabilities and costs

> [P3] Our businesses, have in the past, and may in the future, bring us into contact, directly or indirectly, with individuals and entities that are not within our traditional client and counterparty base, expose us to new asset classes and new markets, and present us with integration challenges. For example, we continue to transact business and invest in new regions, including a wide range of emerging and growth markets, and we expect this trend to continue. Various emerging and growth market countries have experienced severe economic and financial disruptions, including significant devaluations of their currencies, defaults or threatened defaults on sovereign debt, capital and currency exchange

> [P4] Goldman Sachs 2025 Form 10-K THE GOLDMAN SACHS GROUP, INC. AND SUBSIDIARIES As a result of our recovery and resolution planning processes, including incorporating feedback from our regulators, we may incur increased operational, funding or other costs and face limitations on our ability to structure our internal organization or engage in internal or external activities in a manner that we may otherwise deem most operationally efficient. Our commodities activities, particularly our physical commodities activities, subject us to extensive regulation and involve certain potential risks, including environmental, reputational and other risks that may expose us to significant liabilities and costs

> [P5] Goldman Sachs 2024 Form 10-K THE GOLDMAN SACHS GROUP, INC. AND SUBSIDIARIES U.S. and non-U.S. regulatory developments, in particular the Dodd-Frank Act and Basel III, have significantly altered the regulatory framework within which we operate and have adversely affected and may in the future adversely affect our profitability. Among the aspects of the Dodd-Frank Act that have affected or may in the future affect our businesses are: increased capital, liquidity and reporting requirements; limitations on activities in which we may engage; increased regulation of and restrictions on OTC derivatives markets and transactions; limitations on incentive compensation; limitations on affiliate transac

judge: supported

verdict: [ ]

## claim-043  (baseline cross-176)

**Claim:** Higher research and development expense is cited as a factor contributing to the increased loss from operations in the Commercial Airplanes (BCA) segment

> [P1] Commercial Airplanes $2,386 $2,036 $1,510 Defense, Space & Security 917 919 945 Global Services 132 107 119 Other 377 315 278 Total $3,812 $3,377 $2,852 Research and development expense increased by $435 million in 2024 compared with 2023 primarily due to the 777X program at BCA and higher enterprise investments in product development. Research and development expense increased by $525 million in 2023 compared with 2022 primarily due to higher research and development expenditures on the 777X program and enterprise investments in product development.

> [P2] Research and Development The following table summarizes our Research and development expense: (Dollars in millions) Years ended December 31, 2025 2024 2023 Commercial Airplanes $2,202 $2,386 $2,036 Defense, Space & Security 877 917 919 Global Services 125 132 107 Other 411 377 315 Total $3,615 $3,812 $3,377 Research and development expense decreased by $197 million in 2025 compared with 2024. The decrease in expense was primarily due to lower spending at BCA. Research and development expense increased by $435 million in 2024 compared with 2023 primarily due to the 777X program at BCA and higher enterprise investments in product development.

> [P3] Core operating loss increased by $9,982 million in 2024 compared with 2023 and decreased by $2,833 million in 2023 compared with 2022 primarily due to changes in Segment operating loss as described above. Table of Contents Unallocated Items, Eliminations and Other The most significant items included in Unallocated items, eliminations and other (expense)/income are shown in the following table: (Dollars in millions) Years ended December 31, 2024 2023 2022 Share-based plans $171 $62 ($114) Deferred compensation (114) (188) 117 Amortization of previously capitalized interest (93) (95) (95) Research and development expense, net (377) (315) (278) Eliminations and other unallocated items (1,634) (

> [P4] Loss from operations increased by $9,934 million in 2024 compared with 2023. BCA loss from operations increased by $6,334 million primarily due to reach-forward losses on the 777X and 767 programs, 737-9 customer considerations related to the January 2024 grounding, lower deliveries, and lower margins driven by production disruption including the IAM 751 work stoppage and new agreement, and higher research and development expense, partially offset by lower abnormal production costs. BDS loss from operations increased by $3,649 million compared to the same period in 2023 primarily due to higher net unfavorable cumulative contract catch-up adjustments in 2024 on major fixed-price development p

> [P5] The change in Non-cash items of $8.7 billion compared with 2024 was primarily due to a gain on the Digital Aviation Solutions Divestiture in October 2025, partially offset by higher combined 777X and 767 reach-forward losses recorded during 2025 compared to 2024. Changes in assets and liabilities for 2025 improved by $7.8 billion compared to 2024 primarily driven by favorable changes in Inventories ($10.9 billion) and Accounts payable ($1.5 billion), partially offset by unfavorable changes in Advances and progress billings ($4.8 billion). The change in Inventories was primarily driven by higher deliveries on our commercial airplane programs during 2025 as compared to 2024. The change in Acco

judge: supported

verdict: [ ]

## claim-044  (baseline text-143)

**Claim:** If Visa successfully adapts to technological changes by offering its own services, those services may provide less favorable financial terms for the company, which could hurt its financial results

> [P1] Our cybersecurity and processing systems, as well as those of financial institutions, sellers and third-party service providers, have experienced and may continue to experience errors, interruptions, delays or damage from a number of causes including but not limited to, hardware, software and network failures, computer viruses, ransomware, malware or other destructive software, use of AI technologies by bad actors, internal design, manual or user errors, advanced or persistent cyber attacks, social engineering threats, such as phishing or deepfake schemes, including those using synthetic media, insider threats, terrorism, political tensions, war or other military conflicts, or civil unrest,

> [P2] Our competitors may acquire, develop or make better use of substantially better technology, have more widely adopted delivery channels, or have greater financial resources. They may offer more effective, innovative or a wider range of programs, products and services. They may use more effective advertising and marketing strategies that result in broader brand recognition and greater use, including with respect to issuance and seller acceptance. They may also develop better solutions or offer more favorable pricing. Moreover, even if we successfully adapt to technological change and the proliferation of alternative types of payment services by developing and offering our own services in these

> [P3] The global payments industry is undergoing significant and rapid technological change, including increased proliferation of mobile and other proximity and in-app payment technologies, ecommerce, tokenization, cryptocurrencies, distributed ledger and blockchain technologies, cloud-based encryption and authorization, and new authentication technologies such as biometrics, FIDO 2.0, 3D Secure 2.0 and dynamic cardholder verification values or dCVV2. As a result, we expect new services and technologies to continue to emerge and evolve. For example, GenAI and agentic commerce solutions have emerged as an opportunity for Visa, its clients, suppliers, sellers and partners to innovate more quickly an

> [P4] Furthermore, our visibility and role in the global payments industry also puts our company at a greater risk of being targeted by hackers. In the normal course of our business, we have been the target of malicious cyber activity. We have been, and may continue to be, impacted by attacks and data security breaches of financial institutions, merchants, and third-party service providers. We are also aware of instances where governments have directed or sponsored attacks against some of our financial institution clients, and other instances where merchants and issuers have encountered substantial data security breaches affecting their customers, some of whom were Visa account holders. Given the

> [P5] The global payments industry is undergoing significant and rapid technological change, including increased proliferation of mobile and other proximity and in-app payment technologies, ecommerce, tokenization, cryptocurrencies, distributed ledger and blockchain technologies, cloud-based encryption and authorization, and new authentication technologies such as biometrics, FIDO 2.0, 3D Secure 2.0 and dynamic cardholder verification values or dCVV2. As a result, we expect new services and technologies to continue to emerge and evolve, including those developed by Visa such as our new flows offerings. For example, generative AI solutions have emerged as an opportunity for Visa, its clients, suppl

judge: supported

verdict: [ ]

## claim-045  (agent text-141)

**Claim:** The provided evidence does not contain information regarding the primary factors that drove the increase from the 16.5% effective tax rate reported in fiscal 2024

> [P1] 2,910 3,280 (11) Income taxes 5,091 2,090 144 Effective tax rate 19.8 % 16.5 % Gross margin as a percent of revenue in 2025 increased 1.7 percentage points compared with 2024, primarily driven by favorable product mix and improved cost of production, partially offset by lower realized prices. Research and development expenses increased 21 percent in 2025, primarily driven by continued investments in our early and late-stage portfolio. Marketing, selling, and administrative expenses increased 29 percent in 2025, primarily driven by promotional efforts supporting ongoing and planned launches.

> [P2] 3,280.4 3,799.8 (14) Asset impairment, restructuring, and other special charges 860.6 67.7 NM Other—net, (income) expense 218.6 (96.7) NM Income taxes 2,090.4 1,314.2 59 Effective tax rate 16.5 % 20.1 % NM - not meaningful Gross margin as a percent of revenue in 2024 increased 2.1 percentage points compared with 2023, primarily driven by favorable product mix and higher realized prices. Research and development expenses increased 18 percent in 2024, primarily driven by continued investments in our early and late-stage portfolio. Marketing, selling, and administrative expenses increased 16 percent in 2024, primarily driven by promotional efforts supporting ongoing and future launches.

> [P3] Membership and other income increased 13.3% and 7.5% for fiscal 2025 and 2024, respectively, when compared to the previous fiscal year. For fiscal 2025 and 2024, the increases were primarily due to growth in membership base and Plus penetration. Fiscal 2025 and 2024 were also positively impacted by the expiration of a promotional offering offsetting membership fee increases during the fourth quarter of fiscal 2024. Gross profit rate increased 37 and 55 basis points for fiscal 2025 and 2024, respectively, when compared to the previous fiscal year. For fiscal 2025, the increase in gross profit rate was primarily due to improved operational efficiencies related to merchandise flow and increased

> [P4] Percent change 43 % 48 % 45 % In the U.S., the volume increase and the lower realized prices in 2025 were primarily driven by Mounjaro and Zepbound. Outside the U.S., the volume increase in 2025 was primarily driven by Mounjaro. The following table summarizes our revenue, including net product revenue and collaboration and other revenue, by product in 2025 compared with 2024:

> [P5] Our effective income tax rate was 23.4%, 25.5%, and 33.6% for fiscal 2025, 2024 and 2023, respectively. The decrease in effective tax rate in fiscal 2025 compared to fiscal 2024 is primarily due to the tax impact on changes in fair value of our investments. The higher effective tax rate in fiscal 2023 compared to fiscal 2025 and fiscal 2024 is primarily related to the tax impacts of the separation of Flipkart and PhonePe. Our effective income tax rate may also fluctuate as a result of various factors, including changes in our assessment of unrecognized tax benefits, valuation allowances, business operations, acquisitions, investments, entry into new businesses and geographies, intercompany t

> [P6] 36. Table of Contents Alphabet Inc. Provision for Income Taxes The following table presents provision for income taxes (in millions, except effective tax rate): Year Ended December 31, 2024 2025 Income before provision for income taxes $ 119,815 $ 158,826 Provision for income taxes $ 19,697 $ 26,656 Effective tax rate 16.4 % 16.8 % The effective tax rate increased from 2024 to 2025. This increase was primarily due to a decrease in the US Federal Foreign Derived Intangible Income tax deduction, a non-deductible EC fine and legal settlement in the US, partially offset by changes in prior period tax positions. Changes to US tax law enacted on July 4, 2025, allow for immediate expensing of domes

> [F1] ticker = LLY, fiscal_year = 2024, effective_tax_rate = N/A, explanation = The requested metrics (Income Tax Expense and Pre-tax Income) are not available in the provided financial_facts table, therefore the effective tax rate and its year-over-year drivers cannot be calculated.

> [F2] ticker = LLY, fiscal_year = 2025, effective_tax_rate = N/A, explanation = The requested metrics (Income Tax Expense and Pre-tax Income) are not available in the provided financial_facts table, therefore the effective tax rate and its year-over-year drivers cannot be calculated.

judge: supported

verdict: [ ]

## claim-046  (baseline cross-161)

**Claim:** Due to the transition of Comirnaty to commercial markets and the seasonality of demand for COVID‑19 vaccinations, the majority of Pfizer's global revenues for Comirnaty in 2024 were recorded in the fourth quarter.

> [P1] COVID-19––In response to COVID-19, we developed Paxlovid and collaborated with BioNTech to jointly develop Comirnaty. As part of our strategy for COVID-19, we are continuing to make significant investments in breakthrough science. This includes continuing to evaluate Comirnaty and Paxlovid, including against new variants of concern, developing variant adapted vaccine candidates and developing potential combination respiratory vaccines and potential next generation vaccines and therapies. We are also evaluating Paxlovid for certain pediatric patients. See the Product Developments section within MD&A. In 2023, we principally sold Comirnaty globally under government contracts. In September 2023

> [P2] Strategies intended to help mitigate the potential impacts on our business in the short-term have been implemented as well as those outlined in our voluntary agreement with the Trump Administration as discussed above. We are continuing to evaluate opportunities and developing plans which are intended to help mitigate the potential long-term impact of tariffs on our business and operations. For additional information on risks related to our global operations and changes in laws, see the Item 1A. Risk Factors—Global Operations and ––Changes in Laws and Accounting Standards sections. COVID-19––In response to COVID-19, we developed Paxlovid and collaborated with BioNTech to jointly develop Comir

> [P3] Total Revenues––Total revenues decreased $1.0 billion, or 2%, to $62.6 billion in 2025 from $63.6 billion in 2024, reflecting an operational decrease of $1.3 billion, or 2%, partially offset by a favorable impact of foreign exchange of $247 million. The operational decrease was primarily driven by declines in COVID-19 product revenues, partially offset by increases from the Vyndaqel family, Eliquis, Padcev, Lorbrena, Abrysvo and Oncology biosimilars. Excluding contributions from Comirnaty and Paxlovid, Total revenues increased 6% operationally. Pfizer Inc. 2025 Form 10-K The following chart outlines the components of the net change in Total revenues: See the Total Revenues by Geography and T

> [P4] We face risks and uncertainties related to our COVID-19 products, including Comirnaty and Paxlovid or any potential future COVID-19 vaccines, treatments or combinations, including, among others, the risk that as the market for COVID-19 products remains endemic and seasonal, demand for our COVID-19 products has and may continue to be reduced or not meet expectations, which has and may continue to lead to reduced revenues, excess inventory or other unanticipated charges; risks related to our ability to develop and commercialize variant adapted vaccines, combinations and/or treatments; uncertainties related to recommendations and coverage for, and the public’s adherence to, vaccines, boosters,

> [P5] Year Ended December 31, (MILLIONS) 2024 2023 2022 Medicare rebates $ 4,145 $ 997 $ 838 Medicaid and related state program rebates 2,252 1,655 973 Performance-based contract rebates 6,497 5,159 3,575 Chargebacks 12,698 9,828 7,560 Sales allowances 6,444 6,790 5,460 Sales returns and cash discounts 1,852 5,619 1,290 Total(a) $ 33,888 $ 30,048 $ 19,697 (a)The increase in revenue deductions in 2024 was primarily driven by the transition of Paxlovid and Comirnaty to commercial markets, an increase in sales from legacy Seagen products acquired in December 2023, sales growth from the Vyndaqel family, and higher sales of acquired products, partially offset by a $771 million favorable final adjustmen

judge: supported

verdict: [ ]

## claim-047  (agent cross-171)

**Claim:** Strength in eCommerce, strong sales in grocery and health and wellness, and improved sales in general merchandise also contributed.

> [P1] (1)Membership and other income includes membership fees and other items such as rental and tenant income, recycling income, gift card breakage income, as well as other income from corporate campus facilities. (2)Gross profit is defined as net sales less cost of sales. Operating expenses refers to operating, selling, general and administrative expenses. Our total revenues increased $32.2 billion or 4.7% and $32.9 billion or 5.1% for fiscal 2026 and 2025, respectively, when compared to the previous fiscal year. These increases in revenues were primarily due to increases in net sales, which increased $31.9 billion or 4.7% and $31.9 billion or 5.0% for fiscal 2026 and 2025, respectively, when co

> [P2] Membership and other income increased slightly for fiscal 2026 and increased $0.6 billion for fiscal 2025. In both years, the increases were primarily driven by double-digit growth in membership fee revenue from Walmart+. For fiscal 2026, the increase was partially offset by decreases in certain other income items, including a reduction in recycling income. Fiscal 2025 also benefited from higher recycling income compared to the previous fiscal year. Gross profit rate increased 22 and 47 basis points for fiscal 2026 and 2025, respectively, when compared to the previous fiscal year. The increase for fiscal 2026 was primarily driven by disciplined inventory management and growth in higher margi

> [P3] Operating expenses as a percentage of net sales increased 20 and 36 basis points for fiscal 2026 and 2025, respectively, when compared to the previous fiscal year. The increase for fiscal 2026 was primarily due to higher self-insured general liability claims expense in the U.S. of approximately $0.9 billion, influenced by rising costs to resolve claims across retail and related industries, a charge of $0.7 billion related to modification of certain share-based compensation arrangements for our PhonePe subsidiary and increased depreciation related to our capital investments. The increase for fiscal 2025 was primarily due to higher variable pay as a result of exceeding planned performance, inc

> [P4] Membership and other income increased 8.7% and 13.3% for fiscal 2026 and 2025, respectively, when compared to the previous fiscal year. For fiscal 2026 and 2025, the increases were primarily due to growth in the membership base and Plus penetration. Fiscal 2026 was also positively impacted by additional breakage income related to unredeemed Sam's Cash rewards, while fiscal 2025 was positively impacted by the expiration of a promotional offering offsetting membership fee increases during the fourth quarter of fiscal 2024. Gross profit rate increased 4 and 37 basis points for fiscal 2026 and 2025, respectively, when compared to the previous fiscal year. The increase for fiscal 2026 was primari

> [P5] Walmart International is our second largest segment and operates 5,743 stores across 18 countries outside of the U.S. Walmart International operates through our wholly-owned subsidiaries in Canada, Chile, China, and Africa (which includes Botswana, Eswatini, Lesotho, Malawi, Mozambique, Namibia, South Africa and Zambia), and our majority-owned subsidiaries in India, as well as Mexico and Central America (which includes Costa Rica, El Salvador, Guatemala, Honduras and Nicaragua). Walmart International includes numerous formats divided into two major categories: retail and wholesale. These categories consist of many formats, including: supercenters, supermarkets, warehouse clubs (including our

> [P6] Walmart International Segment Fiscal Years Ended January 31, (Dollar amounts and retail square feet in millions) 2026 2025 2024 Net sales $ 130,423 $ 121,885 $ 114,641 Percentage change from comparable period 7.0 % 6.3 % 13.5 % Membership and other income 1,565 1,478 1,408 Gross profit 27,847 26,618 24,810 Operating expenses 24,309 22,595 21,309 Operating income $ 5,103 $ 5,501 $ 4,909 Percentage of net sales Gross profit 21.4 % 21.8 % 21.6 % Operating expenses 18.6 % 18.5 % 18.6 % Operating income 3.9 % 4.5 % 4.3 % Retail unit counts at period end 5,743 5,566 5,402 Retail square feet at period end 278 274 274 Net sales for the Walmart International segment increased $8.5 billion or 7.0% and

> [F1] ticker = WMT, fiscal_year = 2026, metric = revenue, value = 713163000000.0

judge: supported

verdict: [ ]

## claim-048  (baseline text-087)

**Claim:** Lower‑emission fuels are being developed and deployed by LCS

> [P1] Technology and lower-emission solutions. Achieving societal ambitions to reduce greenhouse gas emissions and ultimately achieve net zero will require new technologies and added infrastructure to reduce the cost and increase the scalability of alternative energy sources, as well as technologies such as carbon capture and storage (CCS). CCS technologies, focused initially on capturing and sequestering CO2 emissions from high-carbon intensity industrial activities, can assist in meeting society’s objective to mitigate atmospheric greenhouse gas levels while also helping ensure the availability of the reliable and affordable energy the world requires. ExxonMobil has established a Low Carbon Solu

> [P2] Technology and lower-emission solutions. Achieving societal ambitions to reduce greenhouse gas emissions and ultimately achieve net zero will require new technologies and added infrastructure to reduce the cost and increase the scalability of solutions to reduce emissions, as well as technologies such as carbon capture and storage (CCS). CCS technologies, focused initially on capturing and sequestering CO2 emissions from high-carbon intensity industrial activities, can assist in meeting society’s objective to mitigate atmospheric greenhouse gas levels while also helping to ensure the availability of the reliable and affordable energy the world requires. ExxonMobil has established a Low Carbo

> [P3] As of year-end 2025, we are exceeding our 2030 plans across the portfolio, having already achieved our plans for reducing Corporate greenhouse gas and flaring intensity. We expect to reach the plan for methane intensity reductions later this year. Our emission-reduction plans and 2050 net-zero ambition cover Scope 1 and 2 emissions from assets we operate. The Corporation plans to continue to pursue advantaged growth opportunities and lower-emission investments. These investments are targeted at reducing emissions in the Company’s operations as well as reducing the emissions of other companies. At this early stage, stable and supportive policy remains critical to enable emissions reductions,

> [P4] The Corporation plans to continue to pursue advantaged growth opportunities and lower-emission investments. These investments are targeted at reducing emissions in the Company’s operations as well as reducing the emissions of other companies. At this early stage, stable and supportive policy remains critical to enable emissions reductions, advance technology, and drive scale to improve costs. ExxonMobil’s Low Carbon Solutions business is working with the Product Solutions and Upstream businesses to grow a pipeline of emission-reduction opportunities in carbon capture and storage, hydrogen, lower-emission fuels, ProxximaTM systems, and carbon materials, as well as lithium to supply the global

> [P5] OVERVIEW The following discussion and analysis of ExxonMobil’s financial results, as well as the accompanying financial statements and related notes to consolidated financial statements to which they refer, are the responsibility of the management of Exxon Mobil Corporation. The Corporation’s accounting and financial reporting fairly reflect its integrated business model involving exploration for, and production of, crude oil and natural gas; manufacture, trade, transport and sale of crude oil, natural gas, petroleum products, petrochemicals, and a wide variety of specialty products; and pursuit of lower-emission and other new business opportunities, including carbon capture and storage, hyd

judge: supported

verdict: [ ]

## claim-049  (baseline text-098)

**Claim:** The company maintains this account, from which monetary liabilities from settlements or judgments in U.S. covered litigation are payable.

> [P1] We have entered into loss sharing agreements that reduce our potential liability in connection with certain litigation. However, our U.S. retrospective responsibility plan only addresses monetary liabilities from settlements of, or final judgments in, the U.S. covered litigation. The plan’s mechanisms include the use of the U.S. litigation escrow account. The accrual related to the U.S. covered litigation could be either higher or lower than the U.S. litigation escrow account balance. Our Europe retrospective responsibility plan only covers Visa Europe territory covered litigation (and resultant liabilities and losses) relating to the covered period, subject to certain limitations, and does

> [P2] Assumptions and judgment. We evaluate the likelihood of a potential loss from legal or regulatory proceedings to which we are a party. We record a liability for such claims when a loss is deemed probable and the amount can be reasonably estimated. Significant judgment may be required in the determination of both probability and whether a loss is reasonably estimable. Our judgments are inherently subjective and based on a number of factors, including management’s understanding of the legal or regulatory profile and the specifics of each proceeding, our history with similar matters, advice of internal and external legal counsel and management’s best estimate of incurred loss. As additional inf

> [P3] Under the U.S. retrospective responsibility plan, we recover the monetary liabilities related to the U.S. covered litigation through a downward adjustment to the rate at which shares of our class B-1 and class B-2 common stock ultimately convert into shares of class A common stock. During fiscal 2025, basic and diluted earnings per class A common stock increased $0.01 and was unchanged, respectively, as a result of the downward adjustments of the class B-1 and B-2 common stock conversion rates during the period. During fiscal 2024 and 2023, basic and diluted earnings per class A common stock were unchanged in both fiscal years, as a result of the downward adjustments of the class B-1 and B-2

> [P4] U.S. Litigation escrow account. Pursuant to the terms of the U.S. retrospective responsibility plan, which was created to insulate Visa and our class A common stockholders from financial liability for certain litigation cases, we maintain a U.S. litigation escrow account from which monetary liabilities from settlements of, or judgments in, the U.S. covered litigation will be payable. As these funds are restricted for the sole purpose of making payments related to the U.S. covered litigation matters, we do not rely on them for other operational needs. See Note 5—U.S. and Europe Retrospective Responsibility Plans and Note 20—Legal Matters to our consolidated financial statements included in It

> [P5] Credit facility. We have an unsecured revolving credit facility, which is maintained to ensure the integrity of the payment card settlement process and for general corporate purposes. As of September 30, 2025, there were no amounts outstanding under the credit facility. See Note 10—Debt to our consolidated financial statements included in Item 8 of this report. Senior notes. In May 2025, we issued Euro-denominated fixed-rate senior notes in a public offering in an aggregate principal amount of €3.5 billion ($3.9 billion), with maturities ranging between 3 and 19 years. See Note 10—Debt to our consolidated financial statements included in Item 8 of this report. U.S. Litigation escrow account.

judge: supported

verdict: [ ]

## claim-050  (agent sql-054)

**Claim:** Home Depot's total assets for fiscal year 2023 were $76530000000.0

> [F1] ticker = HD, fiscal_year = 2023, metric = total_assets, value = 76530000000.0

judge: supported

verdict: [ ]

## claim-051  (agent text-152)

**Claim:** ExxonMobil identifies the "capture of efficiencies within and between business lines" as a factor influencing its ability to maintain near‑term cost reductions as ongoing efficiencies without impairing its competitive positioning

> [P1] including timely regulatory approvals; the capture of efficiencies within and between business lines and the ability to maintain near-term cost reductions as ongoing efficiencies without impairing our competitive positioning; unforeseen technical or operating difficulties and unplanned maintenance; the development and competitiveness of alternative energy and emission reduction technologies; consumer preferences including willingness and ability to pay for reduced emission products; the results of research programs and the ability to bring new technologies to commercial scale on a cost-competitive basis; and other factors discussed under Item 1A. Forward-looking and other statements regardin

> [P2] approved; the actions of governments, non-governmental organizations, or other actors against our core business activities and acquisitions, divestitures or financing opportunities; war, civil unrest, armed hostilities, attacks against the Company or industry, and other geopolitical or security disturbances, including disruption of land or sea transportation routes or distribution or shipping channels; decoupling of economies, disruption, realignment, or breaking of current or historical trade or military alliances or global trade or supply chain networks; escalating geopolitical volatility, including regime changes; expropriations, seizures, or capacity, insurance, shipping, import or expor

> [P3] The Upstream capital program is focused on low cost-of-supply opportunities. ExxonMobil has a strong pipeline of development projects, including continued growth in Guyana and the Permian Basin, as well as LNG expansion opportunities in Qatar, Mozambique, Papua New Guinea, and the United States. As future development projects and drilling activities bring new production online, the Corporation expects a shift in the geographic mix and in the type of opportunities from which volumes are produced. Based on the current investment plans, the proportion of oil-equivalent production from the Americas is generally expected to increase over the next several years. Currently about two thirds of the C

> [P4] The term “project” as used in this report can refer to a variety of different activities and does not necessarily have the same meaning as in any government payment transparency reports. Operational efficiency. An important component of ExxonMobil’s competitive performance, especially given the commodity-based nature of many of our businesses, is our ability to operate efficiently, including our ability to manage expenses, improve production yields on an ongoing basis and successfully integrate and achieve the anticipated synergies of acquisitions, including the acquisition of Pioneer. This requires continuous management focus, including technology integration and improvements, cost control,

> [P5] Project and portfolio management. The long-term success of ExxonMobil’s Upstream and Product Solutions businesses, as well as the future success of LCS and other emerging investments, depends on complex, long-term, capital-intensive projects. These projects in turn require a high degree of project management expertise to maximize efficiency. Specific factors that can affect the performance of major projects include our ability to: negotiate successfully with joint venturers, partners, governments, suppliers, customers, or others; protect and enforce our contractual and legal rights, including with our joint venture partners; model and optimize reservoir performance; develop markets for proje

> [P6] Restrictions on doing business. ExxonMobil is subject to laws and sanctions imposed by the United States and by other jurisdictions where we do business that may prohibit ExxonMobil or its affiliates from doing business in certain countries or with certain counterparties or restrict the kind of business that may be conducted, including acquiring and divesting certain assets or importing or exporting certain materials or products. Such restrictions may provide a competitive advantage to competitors who may not be subject to comparable restrictions. Lack of legal certainty. Some countries in which we do business lack well-developed legal systems, lack political or governmental stability, have

judge: supported

verdict: [ ]

## claim-052  (baseline cross-162)

**Claim:** The operating segments most impacted by this currency movement were Latin America; Europe, Middle East and Africa; and Asia Pacific.

> [P1] In 2024, fluctuations in foreign currency exchange rates unfavorably impacted consolidated operating income by 11% due to a stronger U.S. dollar compared to certain foreign currencies, including the Argentine peso, Mexican peso, Brazilian real, Zimbabwean dollar, Turkish lira, Nigerian naira and Japanese yen, which had an unfavorable impact on our Latin America; Europe, Middle East and Africa; and Asia Pacific operating segments. The unfavorable impact of a stronger U.S. dollar compared to the currencies listed above was partially offset by the impact of a weaker U.S. dollar compared to certain other foreign currencies, including the euro and British pound, which had a favorable impact on ou

> [P2] In 2024 and 2023, our operating income was impacted by the weighted-average fluctuations in exchange rates for foreign currencies in which the Company conducted operations (all operating currencies) and for certain individual currencies. These currencies strengthened (weakened) against the U.S. dollar as follows: Year Ended December 31, 2024 2023 All operating currencies (5) % (2) % Australian dollar (1) (5) Brazilian real (7) 3 British pound 3 2 Chinese yuan (2) (7) Euro — 3 Indian rupee (1) (6) Japanese yen (7) (7) Mexican peso (3) 14 Philippine peso (3) (3) South African rand 1 (11) The percentages in the table above do not include the effects of our hedging activities and, therefore, do

> [P3] Year Ended December 31, 2024 2023 Consolidated 21.2 % 24.7 % Europe, Middle East & Africa 55.4 56.8 Latin America 58.5 58.9 North America 23.3 26.4 Asia Pacific 42.3 43.2 Global Ventures 11.5 10.7 Bottling Investments 8.0 7.4 Corporate * * * Calculation is not meaningful. Operating income was $9,992 million in 2024, compared to $11,311 million in 2023, a decrease of $1,319 million, or 12%. The decrease in operating income was primarily driven by higher commodity costs; higher selling, general and administrative expenses; higher other operating charges; the impact of refranchising our bottling operations in the Philippines, Bangladesh and certain territories in India; and an unfavorable forei

> [P4] The Company’s EMEA operating segment reported operating income of $4,298 million and $4,255 million for the years ended December 31, 2025 and 2024, respectively. The increase in operating income was primarily driven by an increase in concentrate sales volume of 4% and favorable pricing initiatives, partially offset by higher commodity costs, increased marketing spending, higher operating expenses, an unfavorable foreign currency exchange rate impact of 5% and the impact of divestiture activity. Latin America reported operating income of $3,742 million and $3,792 million for the years ended December 31, 2025 and 2024, respectively. The decrease in operating income was primarily driven by a de

> [P5] Year Ended December 31, 2025 2024 Consolidated 28.7 % 21.2 % EMEA 39.7 41.4 Latin America 59.1 58.6 North America 25.9 24.1 Asia Pacific 38.3 42.1 Bottling Investments 7.4 8.0 Corporate * * * Calculation is not meaningful. Operating income was $13,762 million in 2025, compared to $9,992 million in 2024, an increase of $3,770 million, or 38%. The increases in operating income and operating margin were primarily driven by lower other operating charges, due to the prior year remeasurement of our contingent consideration liability to fair value in conjunction with the fairlife acquisition, concentrate sales volume growth of 1% and favorable pricing initiatives. These items were partially offset

judge: supported

verdict: [ ]

## claim-053  (agent sql-039)

**Claim:** Meta's long-term debt balance for fiscal 2024 is $28.826 billion

> [F1] ticker = META, fiscal_year = 2024, metric = long_term_debt, value = 28826000000.0

judge: supported

verdict: [ ]

## claim-054  (baseline text-086)

**Claim:** Penalties or other external intervention

> [P1] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P2] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P3] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions, fires, product spills, severe weather, geological events, global health crises, such as epidemics and pandemics, labor disputes, geopolitical tensions, armed hostilities, terrorist or piracy attacks, sabotage, civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater technological challen

> [P4] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions; fires; product spills; severe weather; geological events; global health crises, such as epidemics and pandemics; labor disputes; geopolitical tensions and escalations; armed hostilities; terrorist or piracy attacks; sabotage; civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater techn

> [P5] We are subject to income taxation in numerous jurisdictions worldwide. We record deferred tax assets and liabilities to account for the expected future tax consequences of events that have been recognized in our financial statements and our tax returns. We routinely assess our deferred tax assets and reduce such assets by a valuation allowance if we deem it is more likely than not that some portion, or all, of the deferred tax assets will not be realized. In assessing the need for adjustments to existing valuation allowances, we consider all available positive and negative evidence. Positive evidence includes reversals of temporary differences, forecasts of future taxable income, assessment

judge: supported

verdict: [ ]

## claim-055  (baseline sql-039)

**Claim:** Meta's long-term debt was $28.83 billion as of December 31, 2024.

> [P1] Year Ended December 31, Year Ended December 31, Year Ended December 31, 2024 2023 % change 2024 2023 % change 2024 2023 % change (in millions, except percentages) Revenue $ 162,355 $ 133,006 22% $ 2,146 $ 1,896 13% $ 164,501 $ 134,902 22% Costs and expenses 75,246 70,135 7% 19,875 18,016 10% 95,121 88,151 8% Income (loss) from operations $ 87,109 $ 62,871 39% $ (17,729) $ (16,120) (10)% $ 69,380 $ 46,751 48% Operating margin 54 % 47 % (826) % (850) % 42 % 35 % •Net income was $62.36 billion, with diluted earnings per share (EPS) of $23.86 for the year ended December 31, 2024. •Capital expenditures, including principal payments on finance leases, were $39.23 billion for the year ended Decembe

> [P2] Year Ended December 31, 2024 2023 2022 Net cash provided by operating activities $ 91,328 $ 71,113 $ 50,475 Purchases of property and equipment (37,256) (27,045) (31,186) Principal payments on finance leases (1,969) (1,058) (850) Free cash flow $ 52,103 $ 43,010 $ 18,439 Table of Contents Material Cash Requirements We currently anticipate that our available funds and cash flow from operations and financing activities will be sufficient to meet our operational cash needs and fund our investments in infrastructure and AI initiatives, share repurchases and dividend payments for at least the next 12 months and thereafter for the foreseeable future. We continuously evaluate our liquidity and capi

> [P3] Interest and other income (expense), net in 2024 increased $606 million compared to 2023, mostly due to an increase in interest income from a combination of higher balances and interest rates, partially offset by an increase in interest expense on our long-term debt. Provision for income taxes Year Ended December 31, 2024 2023 2022 2024 vs 2023 % change 2023 vs 2022 % change (in millions, except percentages) Provision for income taxes $ 8,303 $ 8,330 $ 5,619 — % 48 % Effective tax rate 12 % 18 % 19 % Our provision for income taxes in 2024 decreased $27 million compared to 2023, due to a decrease in the effective tax rate, offset by an increase in income before provision for income taxes. Our

> [P4] Our board of directors has authorized a share repurchase program of our Class A common stock, which commenced in January 2017 and does not have an expiration date. In 2024, we repurchased and subsequently retired 65 million shares of our Class A common stock for an aggregate amount of $29.75 billion. As of December 31, 2024, $51.28 billion remained available and authorized for repurchases. Dividend We paid four quarterly cash dividends, including dividend equivalents, totaling $2.00 for each share of Class A and Class B common stock during the year ended December 31, 2024. Total dividends and dividend equivalents paid were $5.07 billion for the year ended December 31, 2024. Subject to legall

> [P5] Interest (Income) Expense: Interest income in the fiscal years 2024 and 2023 was $1.3 billion. Interest expense in the fiscal years 2024 and 2023 was $0.8 billion. Cash, cash equivalents and marketable securities totaled $24.5 billion at the end of 2024, and averaged $23.7 billion as compared to the cash, cash equivalents and marketable securities total of $22.9 billion and $22.6 billion average balance in 2023. The total debt balance at the end of 2024 was $36.6 billion with an average debt balance of $33.0 billion as compared to $29.3 billion at the end of 2023 and an average debt balance of $34.5 billion. The higher debt balance was due to the senior unsecured notes issued by the Company

judge: supported

verdict: [ ]

## claim-056  (baseline adversarial-007)

**Claim:** Dealers are independent, and the reasons for changes in their inventory levels vary, including their expectations of future demand and product delivery times

> [P1] In the first quarter of 2026 as compared to the first quarter of 2025, we expect stronger sales and revenues primarily due to higher sales volume and favorable price realization. We expect higher sales volume to be mainly driven by higher sales of equipment to end users and by the impact from changes in machine dealer inventories. We expect machine dealer inventory to increase in excess of $1.0 billion during the first quarter of 2026, aligning with the seasonal pattern, compared to roughly flat levels in the first quarter of 2025. In the first quarter of 2026 as compared to the first quarter of 2025, we anticipate strong sales growth in Construction Industries, primarily due to higher sales

> [P2] North America sales decreased 1 percent primarily due to lower sales volume, partially offset by favorable price realization. The decrease in sales volume was mainly due to the impact from changes in dealer inventories. Dealer inventory increased less during 2024 than during 2023. Sales increased 1 percent in Latin America. Unfavorable currency impacts related to the Brazilian real were more than offset by higher sales volume and favorable price realization. The increase in sales volume was primarily due to the impact from changes in dealer inventories. Dealer inventory increased during 2024, compared to a decrease during 2023. EAME sales decreased 10 percent primarily due lower sales volume

> [P3] We continue to monitor a variety of external factors around the world, such as supply chain disruptions, inflationary cost and labor pressures. Areas of particular focus include transportation, certain components and raw materials. We continue to work to minimize supply chain challenges that may impact our ability to meet customer demand. We continue to assess the environment to determine if additional actions need to be taken. Risk Factors Risk factors are disclosed within Item 1A. Risk Factors of the 2024 Form 10-K. Notes: •Glossary of terms included on pages 35 - 37; first occurrence of terms shown in bold italics. •Information on non-GAAP financial measures is included on pages 47 - 48.

> [P4] EAME sales increased 4 percent mainly due to higher sales volume and favorable currency impacts related to the euro, partially offset by unfavorable price realization. The increase in sales volume was primarily driven by the impact from changes in dealer inventories. Dealer inventory increased in 2025, compared to a decrease in 2024. Asia/Pacific sales decreased 2 percent primarily due to unfavorable currency impacts related to the Australian dollar, and lower sales volume. The decrease in sales volume was mainly driven by lower sales of equipment to end users. Total dealer inventory increased about $900 million during 2025, compared to an increase of about $400 million during 2024. Machine

> [P5] We sell finished products primarily through an independent dealer network and directly to OEMs and are subject to risks relating to their inventory management decisions and operational and sourcing practices. Both carry inventories of finished products as part of ongoing operations and adjust those inventories based on their assessments of future needs and market conditions, including levels of used equipment inventory and machine rental usage rates. Such adjustments may impact our results positively or negatively. If the inventory levels of our dealers and OEM customers are higher than they desire, they may postpone product purchases from us, which could cause our sales to be lower than the

judge: supported

verdict: [ ]

## claim-057  (baseline text-136)

**Claim:** A paid Target Circle 360 membership provides access to unlimited same‑day delivery on eligible orders over $35, free shipping, extended returns, and exclusive member deals.

> [P1] We generate revenue through a variety of other sources, including Roundel, which provides advertising services to vendors and other third parties, including marketplace sellers; credit card profit sharing related to our Target Circle Card program; our third-party digital marketplace, Target Plus; membership fees; and others. Customer Loyalty Program We seek to drive customer loyalty and trip frequency through our Target Circle™ program, which provides benefits to guests that vary depending on their engagement with the program through one or more of the following offerings: •a free membership providing deals and bonuses including instant discounts and Target Circle Rewards offerings redeemabl

> [P2] (53 weeks) 2024 (52 weeks) 2025 (52 weeks) $107.4 $106.6 $104.8 (a) 2023 consisted of 53 weeks. The extra week in 2023 contributed $1.7 billion of Net Sales. TARGET CORPORATION 2025 Form 10-K 3 BUSINESS Table of Contents Index to Financial Statements Merchandise Sales by Fulfillment Channel Financial Highlights For information on key financial highlights, see Part II, Item 7, Management's Discussion and Analysis of Financial Condition and Results of Operations (MD&A).

> [P3] Strategy Target’s strategy is grounded in our purpose to help all families discover the joy of everyday life and our ambition to be the most delightful experience in retail. We differentiate through design, style, and value, and a curated multi-category assortment delivered across stores and digital channels. Our strategy is centered on four priorities. Lead with Merchandising Authority. Curating design-led, trend-right assortments that combine quality, newness, and value. We focus on categories and brands where we can offer a distinctive and relevant experience for our guests. Elevate the Guest Experience. Elevating the guest experience by making shopping easy, inspiring, and friendly. Our

> [P4] Our year-end cash and cash equivalents balance increased to $5.5 billion from $4.8 billion in 2024. Our cash and cash equivalents balance includes short-term investments of $4.6 billion and $3.9 billion as of January 31, 2026, and February 1, 2025, respectively. Our investment policy is designed to preserve principal and liquidity of our short-term investments. This policy allows investments in large money market funds or in highly rated direct short-term instruments that mature in 60 days or less. We also place dollar limits on our investments in individual funds or instruments. Operating Cash Flows Cash flows provided by operating activities were $6.6 billion in 2025 compared with $7.4 bil

> [P5] Distribution Most merchandise is distributed to our stores through our network of distribution centers. Common carriers ship merchandise to and from our distribution centers. Vendors or third-party distributors ship certain food and beverage items and other merchandise directly to our stores. Merchandise sold through our digital channels is distributed to our guests through guest pick-up at our stores, via common carriers (from stores, supply chain facilities, vendors, and third-party distributors), and same-day delivery. Our stores fulfill the majority of digitally originated sales, which allows improved product availability, faster fulfillment times, reduced shipping costs, and allows us t

judge: supported

verdict: [ ]

## claim-058  (baseline text-135)

**Claim:** In fiscal year 2026, Nvidia invested $17.5 billion in private companies and infrastructure funds

> [P1] Table of Contents We have made, and expect to continue making, investments that support our technology roadmap and the broader AI ecosystem. In fiscal year 2026, we made the following investments: •We invested $17.5 billion in private companies and infrastructure funds, primarily to support early‑stage startups. These investments include AI model makers that purchase our products directly or through CSPs. Many of these investments are illiquid and non‑marketable. The related early-stage startups may not become profitable in the near term, or at all, and there can be no assurance that we will realize a return on our investments. •We made investments in publicly-held equity securities where th

> [P2] During fiscal year 2026 and fiscal year 2025, we spent $6.1 billion and $3.4 billion on capital expenditures, respectively. We expect to increase capital expenditures in fiscal year 2027 relative to fiscal year 2026 to support the future growth of our business. Unrecognized tax benefits of $4.0 billion, which includes related interest and penalties of $374 million, were recorded in non-current income tax payable at the end of fiscal year 2026. We are unable to estimate the timing of any potential tax liability, interest payments, or penalties in individual years due to uncertainties in the underlying income tax positions and the timing of the effective settlement of such tax positions. We ar

> [P3] Cash provided by operating activities increased in fiscal year 2026 compared to fiscal year 2025, due to higher revenue. Cash used in investing activities increased in fiscal year 2026 compared to fiscal year 2025, primarily driven by higher purchases of equity investment securities and the execution of a non-exclusive license agreement with Groq. Cash used in financing activities increased in fiscal year 2026 compared to fiscal year 2025, mainly due to higher share repurchases. Liquidity Our primary sources of liquidity include cash, cash equivalents, marketable securities, and cash generated by our operations. As of January 25, 2026, we had $62.6 billion in cash, cash equivalents, and mark

> [P4] Compute & Networking $ 130,141 $ 82,875 $ 47,266 57 % Graphics 9,156 5,085 4,071 80 % Total $ 139,297 $ 87,960 $ 51,337 58 % Compute & Networking revenue – The year over year increase was driven by the major platform shifts – accelerated computing and AI. Revenue from Data Center computing grew 59% driven by demand for our Blackwell computing platform. Revenue from Data Center networking grew 142% driven by the introduction and continued ramp of NVLink compute fabric for GB200 and GB300 systems and the growth of Ethernet and InfiniBand platforms. Graphics revenue – The year over year increase was driven by sales of our Blackwell architecture. Reportable segment operating income – The year ov

> [P5] Except for approximately $1.7 billion of cash, cash equivalents, and marketable securities held outside the U.S. for which we have not accrued any related foreign or state taxes if we repatriate these amounts to the U.S., substantially all of our cash, cash equivalents and marketable securities held outside the U.S. at the end of fiscal year 2026 are available for use in the U.S. without incurring additional U.S. federal income taxes. Our first quarter of any fiscal year (including fiscal year 2027) generally does not include any estimated federal and state income tax payments and our second quarter of any fiscal year (including fiscal year 2027) generally includes two estimated federal and

judge: supported

verdict: [ ]

## claim-059  (baseline text-084)

**Claim:** The total amount of Class A and Class C share repurchases by Alphabet for the year ended December 31, 2025, was $45.4 billion

> [P1] Other Information: 32. Table of Contents Alphabet Inc. •In 2025, we entered into definitive agreements to acquire Wiz, a leading cloud security platform, for $32.0 billion, and Intersect, a provider of data center and energy infrastructure solutions, for $4.8 billion in cash plus the assumption of debt. Both acquisitions are expected to close in 2026, subject to customary closing conditions, including the receipt of regulatory approvals. •In 2025, we issued senior unsecured notes for net proceeds of $37.3 billion, to be used for general corporate purposes. •OI&E of $29.8 billion for the year ended December 31, 2025 included net gains on equity securities of $24.1 billion, primarily related t

> [P2] As of December 31, 2025, we had $10.0 billion of revolving credit facilities, $4.0 billion expiring in April 2026 and $6.0 billion expiring in April 2030. No amounts have been borrowed under the credit facilities. We also have a commercial paper program of up to $25.0 billion, which is used for general corporate purposes. As of December 31, 2025, we had no commercial paper outstanding. For additional information, see Note 6 of the Notes to Consolidated Financial Statements included in Item 8 of this Annual Report on Form 10-K. We use contract manufacturers for our technical infrastructure and device assembly and may supply them with components purchased directly from suppliers. Certain of th

> [P3] We primarily utilize contract manufacturers for the assembly of our servers used in our technical infrastructure and devices we sell. We have agreements where we may purchase components directly from suppliers and then supply these components to contract manufacturers for use in the assembly of the servers and devices. Certain of these arrangements result in a portion of the cash received from and paid to the contract manufacturers to be presented as financing activities in the Consolidated Statements of Cash Flows included in Item 8 of this Annual Report on Form 10-K. Share Repurchase Program During 2024, we repurchased and subsequently retired 379 million shares for $62.0 billion. In April

> [P4] In April 2025, the company's Board of Directors increased the quarterly cash dividend by 5% to $0.21 per share of outstanding Class A, Class B, and Class C shares. The company has declared a quarterly cash dividend in the current quarter, and intends to pay quarterly cash dividends in the future, subject to review and approval by the company’s Board of Directors in its sole discretion. Accrued Legal and Regulatory As of December 31, 2025, we had short-term accrued legal and regulatory fines and settlements of $15.6 billion. This amount primarily included EC fines, in addition to accruals related to other legal matters and regulatory fines and settlements. For additional information, see Note

> [P5] Our Class B stock has 10 votes per share, our Class A stock has one vote per share, and our Class C stock has no voting rights. As of December 31, 2025, Larry Page and Sergey Brin beneficially owned approximately 89.3% of our 21. Table of Contents Alphabet Inc. outstanding Class B stock, which represented approximately 52.7% of the voting power of our outstanding common stock. Through their stock ownership, Larry and Sergey have significant influence over all matters requiring stockholder approval, including the election of directors and significant corporate transactions, such as a merger or other sale of our company or our assets, for the foreseeable future. In addition, because our Class

judge: supported

verdict: [ ]

## claim-060  (agent text-099)

**Claim:** Claims may emerge in future years for events that occurred in a prior policy period at a rate that differs from actuarial projections, potentially increasing costs

> [P1] Insurance and claims expense could materially adversely affect us. We have a combination of both self-insurance and high-deductible insurance programs for the risks arising out of our business and operations, including claims exposure resulting from cargo loss, cyber-attacks, personal injury, property damage, aircraft and related liabilities, business interruption and workers' compensation. Self-insured workers' compensation, automobile and general liabilities are determined using actuarial estimates of the aggregate liability for claims incurred and an estimate of incurred but not reported claims, on an undiscounted basis. Our accruals for insurance reserves reflect certain actuarial assump

> [P2] Insurance and claims expense could materially adversely affect us. We have a combination of both self-insurance and high-deductible insurance programs for the risks arising out of our business and operations, including claims exposure resulting from cargo loss, cyber-attacks, personal injury, property damage, aircraft and related liabilities, business interruption and workers' compensation. Self-insured workers' compensation, automobile and general liabilities are determined using actuarial estimates of the aggregate liability for claims incurred and an estimate of incurred but not reported claims, on an undiscounted basis. Our accruals for insurance reserves reflect certain actuarial assump

> [P3] Workers' compensation, automobile liability and general liability insurance claims may take a number of years to resolve. Consequently, actuarial estimates are required to project the ultimate cost that will be incurred to resolve a claim. Several factors can affect the actual cost, or severity, of a claim, including: •Risk retention limits; •Length of time a claim remains open; •Trends in healthcare and litigation costs; •Results of any related litigation; and •Changes in legislation. UNITED PARCEL SERVICE, INC. AND SUBSIDIARIES MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS Furthermore, claims may emerge in future years for events that occurred in a p

> [P4] Our finite-lived intangible assets are amortized over their estimated useful lives. These assets are tested for impairment as part of asset groups that may include other long-lived assets. See "Critical Accounting Estimates – Depreciation, Residual Value and Impairment of Property, Plant and Equipment" for a discussion of estimates impacting asset groups. In addition, a reduction in expected useful life, or a decision to sell or abandon an intangible asset before the end of its useful life, may increase amortization expense, which could have a material impact on our results of operations. UNITED PARCEL SERVICE, INC. AND SUBSIDIARIES MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION

> [P5] We are predominantly self-insured for a number of different risk categories, such as general liability (including product liability), property loss, workers’ compensation, employee group medical, employment practices liability and wage and hour claims, automobile claims, and cybersecurity and privacy liability, with insurance coverage for certain catastrophic risks above the self-insurance levels. The types and amounts of insurance may vary from time to time based on our decisions with respect to risk retention and regulatory requirements. The occurrence of significant claims, a substantial rise in costs to maintain our insurance, the failure to maintain adequate insurance coverage, or dispu

> [P6] Due to the complexity and inherent uncertainty associated with the estimation of our workers’ compensation, automobile and general claims liabilities, the third-party actuary develops a range of expected losses. We believe our estimated reserves for such claims are adequate; however, actual experience in claims frequency and/or severity of claims could materially differ from our estimates and affect our results of operations. We also sponsor several health and welfare insurance plans for our employees. Liabilities and expenses related to these plans are based on estimates of the number of employees and eligible dependents covered under the plans, global health events, anticipated utilization

judge: supported

verdict: [ ]

## claim-061  (agent adversarial-007)

**Claim:** Conversely, if dealers do not maintain sufficient inventory, Caterpillar may lose time-sensitive sales

> [P1] In the first quarter of 2026 as compared to the first quarter of 2025, we expect stronger sales and revenues primarily due to higher sales volume and favorable price realization. We expect higher sales volume to be mainly driven by higher sales of equipment to end users and by the impact from changes in machine dealer inventories. We expect machine dealer inventory to increase in excess of $1.0 billion during the first quarter of 2026, aligning with the seasonal pattern, compared to roughly flat levels in the first quarter of 2025. In the first quarter of 2026 as compared to the first quarter of 2025, we anticipate strong sales growth in Construction Industries, primarily due to higher sales

> [P2] North America sales decreased 1 percent primarily due to lower sales volume, partially offset by favorable price realization. The decrease in sales volume was mainly due to the impact from changes in dealer inventories. Dealer inventory increased less during 2024 than during 2023. Sales increased 1 percent in Latin America. Unfavorable currency impacts related to the Brazilian real were more than offset by higher sales volume and favorable price realization. The increase in sales volume was primarily due to the impact from changes in dealer inventories. Dealer inventory increased during 2024, compared to a decrease during 2023. EAME sales decreased 10 percent primarily due lower sales volume

> [P3] We continue to monitor a variety of external factors around the world, such as supply chain disruptions, inflationary cost and labor pressures. Areas of particular focus include transportation, certain components and raw materials. We continue to work to minimize supply chain challenges that may impact our ability to meet customer demand. We continue to assess the environment to determine if additional actions need to be taken. Risk Factors Risk factors are disclosed within Item 1A. Risk Factors of the 2024 Form 10-K. Notes: •Glossary of terms included on pages 35 - 37; first occurrence of terms shown in bold italics. •Information on non-GAAP financial measures is included on pages 47 - 48.

> [P4] EAME sales increased 4 percent mainly due to higher sales volume and favorable currency impacts related to the euro, partially offset by unfavorable price realization. The increase in sales volume was primarily driven by the impact from changes in dealer inventories. Dealer inventory increased in 2025, compared to a decrease in 2024. Asia/Pacific sales decreased 2 percent primarily due to unfavorable currency impacts related to the Australian dollar, and lower sales volume. The decrease in sales volume was mainly driven by lower sales of equipment to end users. Total dealer inventory increased about $900 million during 2025, compared to an increase of about $400 million during 2024. Machine

> [P5] We sell finished products primarily through an independent dealer network and directly to OEMs and are subject to risks relating to their inventory management decisions and operational and sourcing practices. Both carry inventories of finished products as part of ongoing operations and adjust those inventories based on their assessments of future needs and market conditions, including levels of used equipment inventory and machine rental usage rates. Such adjustments may impact our results positively or negatively. If the inventory levels of our dealers and OEM customers are higher than they desire, they may postpone product purchases from us, which could cause our sales to be lower than the

> [P6] We sell finished products primarily through an independent dealer network and directly to OEMs and are subject to risks relating to their inventory management decisions and operational and sourcing practices. Both carry inventories of finished products as part of ongoing operations and adjust those inventories based on their assessments of future needs and market conditions, including levels of used equipment inventory and machine rental usage rates. Such adjustments may impact our results positively or negatively. If the inventory levels of our dealers and OEM customers are higher than they desire, they may postpone product purchases from us, which could cause our sales to be lower than the

judge: supported

verdict: [ ]

## claim-062  (agent sql-050)

**Claim:** Alphabet's revenue in fiscal 2025 was $402.84 billion

> [F1] ticker = GOOGL, fiscal_year = 2025, metric = revenue, value = 402836000000.0

judge: supported

verdict: [ ]

## claim-063  (agent text-085)

**Claim:** In November 2024, PF-07926307 (COVID-19/mRNA flu combo vaccine) reverted from Phase 3 to Phase 1 clinical trials

> [P1] (b)Eliquis is being developed in collaboration with BMS. (c)Padcev is being jointly developed and commercialized with Astellas. (d)VLA15 is being developed in collaboration with Valneva SE. (e)Vepdegestrant is being developed in collaboration with Arvinas. (f)Disitamab vedotin is being developed in collaboration with RemeGen Co., Ltd. Pfizer Inc. 2024 Form 10-K In December 2024, Pfizer decided to terminate development of giroctocogene fitelparvovec (PF-07055480) and elected to terminate the collaboration and license agreement between Pfizer and Sangamo Therapeutics, Inc. effective as of April 21, 2025. In August 2024, Pfizer announced Phase 3 top-line results for Pfizer and BioNTech’s combin

> [P2] Approved April 2024 Filed February 2024 Filed April 2024 Comirnaty (COVID-19 Vaccine, mRNA) 2024-2025 Formula, Omicron KP.2-adapted(i) Active immunization to prevent COVID-19 caused by SARS-CoV-2 for individuals 12 years of age and older Approved August 2024 Approved September 2024 Comirnaty (COVID-19 Vaccine, mRNA) 2024-2025 Formula, Omicron JN.1-adapted Active immunization to prevent COVID-19 caused by SARS-CoV-2 for individuals 6 months of age and older Approved July 2024 Approved August 2024 Adcetris (brentuximab vedotin)(j) Relapsed/refractory diffuse large B-cell lymphoma Approved

> [P3] Pfizer Inc. 2025 Form 10-K Our R&D Pipeline. The process of drug, vaccine and biological product discovery from initiation through development and to potential regulatory approval is lengthy and can take more than ten years. As of February 3, 2026, we had the following number of projects in various stages of R&D: Development of a single compound is often pursued as part of multiple programs. While our product candidates may or may not receive regulatory approval, new candidates entering clinical development phases are the foundation for future products. Information concerning several of our drug, vaccine and biological candidates in development, as well as supplemental filings for existing p

> [P4] (d)Being jointly developed and commercialized with Astellas. (e)Being developed in collaboration with AbbVie. AbbVie has the exclusive commercialization rights in the U.S. and Canada; Pfizer leads the joint development program and has commercialization rights in all other countries. (f)Being jointly developed and commercialized with Astellas. (g)Keytruda® is a registered trademark of Merck Sharp & Dohme Corp., a subsidiary of Merck & Co., Inc. (h)Being developed in collaboration with Genmab A/S. The April 2024 approval date in the U.S. refers to the conversion of a prior accelerated approval to full approval. (i)In September 2024, the EC approved the Pfizer/BioNTech Omicron KP.2-adapted mono

> [P5] •Comirnaty is an mRNA-based coronavirus vaccine to help prevent COVID-19, which is being jointly developed and commercialized with BioNTech. Pfizer and BioNTech equally share the costs of development for the Comirnaty program. Comirnaty has been granted an approval or an authorization in many countries around the world in populations varying by country. We also share gross profits equally from commercialization of Comirnaty (excluding China, Hong Kong, Macau and Taiwan, where we do not have rights), subject to regulatory authorizations or approvals market by market. For discussion on Comirnaty, see the Overview of Our Performance, Operating Environment, Strategy and Outlook—COVID-19 section

> [P6] MK-7962, Winrevair, Merck’s novel activin signaling inhibitor, is under review in Japan for the treatment of adult patients with PAH based on the Phase 3 STELLAR trial. In November 2024, Merck announced positive topline results from the Phase 3 ZENITH study, evaluating Winrevair in adults with PAH with WHO Group 1 FC III or IV at high risk of mortality. Based on the positive results of an interim analysis, an independent data monitoring committee recommended that the study be stopped early due to overwhelming efficacy. In addition, in January 2025, Merck announced the Phase 3 HYPERION study evaluating Winrevair in newly diagnosed adults with PAH FC II or III at intermediate or high risk of d

judge: supported

verdict: [ ]

## claim-064  (baseline text-087)

**Claim:** Advanced energy‑saving materials and carbon materials are focus areas of LCS

> [P1] Technology and lower-emission solutions. Achieving societal ambitions to reduce greenhouse gas emissions and ultimately achieve net zero will require new technologies and added infrastructure to reduce the cost and increase the scalability of alternative energy sources, as well as technologies such as carbon capture and storage (CCS). CCS technologies, focused initially on capturing and sequestering CO2 emissions from high-carbon intensity industrial activities, can assist in meeting society’s objective to mitigate atmospheric greenhouse gas levels while also helping ensure the availability of the reliable and affordable energy the world requires. ExxonMobil has established a Low Carbon Solu

> [P2] Technology and lower-emission solutions. Achieving societal ambitions to reduce greenhouse gas emissions and ultimately achieve net zero will require new technologies and added infrastructure to reduce the cost and increase the scalability of solutions to reduce emissions, as well as technologies such as carbon capture and storage (CCS). CCS technologies, focused initially on capturing and sequestering CO2 emissions from high-carbon intensity industrial activities, can assist in meeting society’s objective to mitigate atmospheric greenhouse gas levels while also helping to ensure the availability of the reliable and affordable energy the world requires. ExxonMobil has established a Low Carbo

> [P3] As of year-end 2025, we are exceeding our 2030 plans across the portfolio, having already achieved our plans for reducing Corporate greenhouse gas and flaring intensity. We expect to reach the plan for methane intensity reductions later this year. Our emission-reduction plans and 2050 net-zero ambition cover Scope 1 and 2 emissions from assets we operate. The Corporation plans to continue to pursue advantaged growth opportunities and lower-emission investments. These investments are targeted at reducing emissions in the Company’s operations as well as reducing the emissions of other companies. At this early stage, stable and supportive policy remains critical to enable emissions reductions,

> [P4] The Corporation plans to continue to pursue advantaged growth opportunities and lower-emission investments. These investments are targeted at reducing emissions in the Company’s operations as well as reducing the emissions of other companies. At this early stage, stable and supportive policy remains critical to enable emissions reductions, advance technology, and drive scale to improve costs. ExxonMobil’s Low Carbon Solutions business is working with the Product Solutions and Upstream businesses to grow a pipeline of emission-reduction opportunities in carbon capture and storage, hydrogen, lower-emission fuels, ProxximaTM systems, and carbon materials, as well as lithium to supply the global

> [P5] OVERVIEW The following discussion and analysis of ExxonMobil’s financial results, as well as the accompanying financial statements and related notes to consolidated financial statements to which they refer, are the responsibility of the management of Exxon Mobil Corporation. The Corporation’s accounting and financial reporting fairly reflect its integrated business model involving exploration for, and production of, crude oil and natural gas; manufacture, trade, transport and sale of crude oil, natural gas, petroleum products, petrochemicals, and a wide variety of specialty products; and pursuit of lower-emission and other new business opportunities, including carbon capture and storage, hyd

judge: supported

verdict: [ ]

## claim-065  (baseline text-132)

**Claim:** Apple identifies the ability to effectively protect and enforce its intellectual property rights as a principal competitive factor important to its success

> [P1] The markets for the Company’s products and services are highly competitive and are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. The markets in which the Company competes are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements by competitors. Many of the Company’s competitors seek to compete primarily through aggressive pricing and very low cost structures, and by imitating the Company’s products and infringing on its intellec

> [P2] The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs and develops nearly the entire solution for its products, including the hardware, operating system, numerous software applications and related services. Principal competitive factors important to the Company include price, product and service features (including security features), relative price and performance, product and service quality and reliability, design innovation, a strong third-party software and accessories ecosystem, marketing and distribution capability, service and suppor

> [P3] The Company’s products and services are offered in highly competitive global markets. These markets are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. These markets are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements. The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs an

> [P4] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number of factors, including timely and successful development, market accepta

> [P5] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, navigate global regulatory requirements and barriers to market access, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number

judge: supported

verdict: [ ]

## claim-066  (baseline text-156)

**Claim:** Higher sales volumes (inclusive of volumes from the acquisition of Marathon Oil) offset lower crude prices

> [P1] Millions of Dollars Years Ended December 31 2025 2024 2023 Sales and other operating revenues $ 58,944 54,745 56,141 Equity in earnings of affiliates 1,335 1,705 1,720 Gain (loss) on dispositions 731 51 228 Purchased commodities 22,325 20,012 21,975 Production and operating expenses 10,331 8,751 7,693 Selling, general and administrative expenses 893 1,158 705 Depreciation, depletion and amortization 11,500 9,599 8,270 Other expenses 20 181 2 Income tax provision (benefit) 4,668 4,427 5,331 Sales and other operating revenues increased $4,199 million in 2025, primarily due to higher volumes of $6,197 million, inclusive of sales volumes from our acquisition of Marathon Oil and higher realized g

> [P2] Net Income (Loss) Lower 48 reported earnings of $5,264 million in 2025, compared with earnings of $5,175 million in 2024. Increases to earnings included higher revenues resulting from higher volumes of $3,890 million, inclusive of volumes from our acquisition of Marathon Oil, partly offset by lower commodity prices of $1,999 million, driven by lower crude prices. Additional increases included higher gains on dispositions of $494 million, primarily associated with the divestitures of the Ursa and Europa fields and Ursa Oil Pipeline Company LLC, and other noncore assets. Decreases to earnings included higher DD&A of $1,330 million and higher production and operating expenses of $875 million, p

> [P3] Net Income (Loss) The Europe, Middle East and North Africa segment reported earnings of $1,224 million in 2025 compared with earnings of $1,189 million in 2024. Earnings in 2025 included higher revenues resulting from higher volumes of $296 million, including volumes from our Equatorial Guinea assets from the acquisition of Marathon Oil, partly offset by lower overall realized commodity prices of $185 million, driven by lower crude prices. See Note 3. Decreases to earnings included higher production and operating expenses of $88 million, primarily from our acquisition of Marathon Oil. See Note 3. Consolidated Production Average consolidated production increased 40 MBOED in 2025, compared wit

> [P4] Crude and bitumen prices were lower through 2025 as global oil supplies increased faster than global oil demand. Natural gas prices increased due to stronger demand and lower inventory levels relative to 2024. Our worldwide annual average realized price decrease was driven by lower crude and bitumen prices. ConocoPhillips 2025 10-K Management’s Discussion and Analysis Table of Contents Key Operating and Financial Summary Significant items during 2025 and recent announcements included the following: •Reported fourth-quarter 2025 earnings per share of $1.17; •Generated cash provided by operating activities of $19.8 billion; •Distributed $9.0 billion to shareholders, including $5.0 billion thro

> [P5] At December 31, 2025, we had cash and cash equivalents of $6.5 billion, short-term investments of $0.5 billion, and available borrowing capacity under our credit facility of $5.5 billion, totaling approximately $12.5 billion of liquidity. In addition, we have long-term investments in debt securities of $1.1 billion. We believe current cash balances and cash generated by operations, together with access to external sources of funds as described below in the “Significant Changes in Capital” section, will be sufficient to meet our funding requirements in the near- and long-term, including our capital spending program, capital return program and required debt payments. Significant Changes in Cap

judge: supported

verdict: [ ]

## claim-067  (baseline cross-185)

**Claim:** Alliance revenue related to Lynparza grew 11% in 2025, largely due to higher global demand

> [P1] Lynparza is a PARP inhibitor being developed and commercialized as part of a collaboration with AstraZeneca (see Note 4 to the consolidated financial statements). Lynparza is approved for the treatment of certain types of advanced or recurrent ovarian, early or metastatic breast, metastatic pancreatic and metastatic castration-resistant prostate cancers. Alliance revenue related to Lynparza grew 11% in 2025 largely due to higher demand globally. In January 2025, China’s NMPA approved Lynparza as adjuvant treatment for adult patients with germline BRCA-mutated, HER2-negative high-risk early breast cancer, based on the OlympiA trial. Lenvima is an oral receptor TKI being developed and commerci

> [P2] Worldwide sales were $65.0 billion in 2025, representing growth of 1% compared with 2024, or 2% excluding the unfavorable effect of foreign exchange. Global sales growth was primarily due to higher sales in the oncology franchise, largely due to the performance of Keytruda and Welireg, as well as increased alliance revenue from Koselugo (resulting from an amendment to the collaboration agreement), Reblozyl, and Lynparza. Also contributing to revenue growth in 2025 were higher sales in the cardiometabolic and respiratory franchise, largely attributable to the ongoing launch of Winrevair, as well as the inclusion of Ohtuvayre sales following the October 2025 acquisition of Verona Pharma. Growt

> [P3] Sales in the U.S. grew 13% to $36.5 billion in 2025 primarily driven by higher sales of Keytruda, Winrevair, Capvaxive, Januvia, Bridion, Gardasil 9, Welireg, Janumet, and Prevymis. The inclusion of Ohtuvayre sales, higher alliance revenue from Reblozyl, and higher sales of animal health products also contributed to U.S. revenue growth. U.S. sales growth in 2025 was partially offset by lower sales of Dificid and Lagevrio. International sales declined 11% in 2025, or 10% excluding the unfavorable effect of foreign exchange. The international sales decline was primarily due to lower sales of Gardasil/Gardasil 9, Simponi, Lagevrio, Januvia, Bridion, Remicade, and Janumet, partially offset by hi

> [P4] Keytruda/Keytruda Qlex 31,680 29,482 25,011 Gardasil/Gardasil 9 5,233 8,583 8,886 Januvia/Janumet 2,544 2,268 3,366 ProQuad/M-M-R II/Varivax 2,451 2,485 2,368 Bridion 1,841 1,764 1,842 Alliance revenue - Lynparza(1) 1,450 1,311 1,199 Winrevair 1,443 419 — Alliance revenue - Lenvima(1) 1,053 1,010 960 Prevymis 978 785 605 Vaxneuvance 825 808 665 Capvaxive 759 97 — Welireg 716 509 218 Animal Health 6,354 5,877 5,625 Livestock 3,896 3,462 3,337 Companion Animal 2,458 2,415 2,288 Other Revenues(2)

> [P5] (1) Alliance revenue for Lynparza and Lenvima represents Merck’s share of profits, which are product sales net of cost of sales and commercialization costs (see Note 4 to the consolidated financial statements). (2) Alliance revenue for Reblozyl represents royalties (see Note 4 to the consolidated financial statements). (3) Alliance revenue for Koselugo in 2025 primarily includes a $150 million upfront payment received and $175 million of regulatory approval milestones recorded in connection with an amendment to the collaboration agreement with AstraZeneca, which revised the payment structure. Alliance revenue in 2024 and 2023 represents Merck’s share of profits, which are product sales net o

judge: supported

verdict: [ ]

## claim-068  (baseline text-088)

**Claim:** Keytruda is approved as monotherapy for urothelial cancer, including non-muscle invasive bladder cancer

> [P1] Pharmaceutical The Pharmaceutical segment includes human health pharmaceutical and vaccine products. Human health pharmaceutical products consist of therapeutic and preventive agents, generally sold by prescription, for the treatment of human disorders. Human health vaccine products consist of preventive pediatric, adolescent and adult vaccines. Certain of the products within the Company’s franchises are as follows: Table of Contents Oncology Keytruda is an anti-PD-1 (programmed death receptor-1) therapy that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroeso

> [P2] The Company received more than 25 regulatory approvals in major markets in 2024, including the Winrevair and Capvaxive approvals noted above, along with numerous approvals in oncology. Keytruda received approval for additional indications in the U.S. and/or internationally as monotherapy in the therapeutic areas of hepatocellular carcinoma (HCC), melanoma and urothelial carcinoma, in combination with chemotherapy in the therapeutic areas of biliary tract cancer, cervical cancer, endometrial carcinoma, gastric or gastroesophageal junction (GEJ) adenocarcinoma, malignant pleural mesothelioma and non-small-cell lung cancer (NSCLC), as well as in combination with Padcev (enfortunab vedotin-ejfv)

> [P3] MK-3475, Keytruda, is an anti-PD-1 therapy approved for the treatment of many cancers that is in clinical development for expanded indications. These studies encompass more than 30 cancer types including: biliary, estrogen receptor positive breast, triple-negative breast, cervical, colorectal, endometrial, esophageal, gastric, glioblastoma, head and neck, hepatocellular, Hodgkin lymphoma, non-Hodgkin lymphoma, non-small-cell lung, small-cell lung, melanoma, malignant pleural mesothelioma, ovarian, prostate, renal, and urothelial, several of which are currently in Phase 3 clinical development. Further trials are being planned for other cancers. Keytruda is under review in the EU and Japan for

> [P4] Keytruda (pembrolizumab) is an anti-PD-1 (programmed death receptor-1) therapy available for intravenous administration that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroesophageal junction (GEJ) carcinoma, head and neck squamous cell carcinoma (HNSCC), hepatocellular carcinoma (HCC), melanoma, Merkel cell carcinoma, microsatellite instability-high (MSI-H) or mismatch repair deficient (dMMR) solid tumors (including MSI-H/dMMR colorectal cancer and endometrial carcinoma), non-small cell lung cancer (NSCLC), primary mediastinal large B-cell lymphoma (PMBCL),

> [P5] Disease (JPN) Pneumococcal Vaccine Adult V116 Capvaxive (EU) (JPN) Pulmonary Arterial Hypertension MK-7962 Winrevair (JPN) Respiratory Syncytial Virus MK-1654 (clesrovimab) (U.S.) (EU) Certain Supplemental Filings Cancer MK-3475 Keytruda • First-Line Unresectable Advanced or Metastatic Malignant Pleural Mesothelioma (KEYNOTE-483) (EU) (JPN) MK-6482 Welireg • Advanced, Unresectable, or Metastatic Pheochromocytoma and Paraganglioma (LITESPARK-015) (U.S.) Footnotes: (1) Being developed in a collaboration. (2) Being developed in combination with Keytruda. (3) Being developed as monotherapy and/or in combination with Keytruda. (4) FDA lifted clinical hold on December 4, 2024. (5) On FDA partial c

judge: supported

verdict: [ ]

## claim-069  (baseline cross-175)

**Claim:** Walmart's total capital expenditures for fiscal 2025 were $23,783 million

> [P1] We define free cash flow as net cash provided by operating activities in a period minus payments for property and equipment made in that period. We had net cash provided by operating activities of $36.4 billion, $35.7 billion and $28.8 billion for fiscal 2025, 2024 and 2023, respectively. We generated free cash flow of $12.7 billion, $15.1 billion and $12.0 billion for fiscal 2025, 2024 and 2023, respectively. The increase in net cash provided by operating activities in fiscal 2025 is primarily due to an increase in cash provided by operating income and lapping the payment of accrued opioid legal charges in the prior year, partially offset by increased inventory purchases. Free cash flow for

> [P2] Fiscal Years Ended January 31, (Amounts in millions) 2026 2025 2024 Net cash provided by operating activities $ 41,565 $ 36,443 $ 35,726 Payments for property and equipment (26,642) (23,783) (20,606) Free cash flow $ 14,923 $ 12,660 $ 15,120 Net cash used in investing activities(1) $ (26,350) $ (21,379) $ (21,287) Net cash used in financing activities (13,553) (14,822) (13,414) (1)"Net cash used in investing activities" includes payments for property and equipment, which is also included in our computation of free cash flow. The increase in net cash provided by operating activities in fiscal 2026 is primarily due to an increase in cash provided by operating income, lower cash tax payments an

> [P3] (Amounts in millions) Fiscal Years Ended January 31, Allocation of Capital Expenditures 2025 2024 Supply chain, customer-facing initiatives, technology and other $ 14,603 $ 11,828 Store and club remodels 5,552 5,792 New stores and clubs, including expansions and relocations 450 75 Total U.S. $ 20,605 $ 17,695 Walmart International 3,178 2,911 Total Capital Expenditures $ 23,783 $ 20,606 Free Cash Flow Free cash flow is considered a non-GAAP financial measure. Management believes, however, that free cash flow, which measures our ability to generate additional cash from our business operations, is an important financial measure for use in evaluating the Company's financial performance. Free ca

> [P4] (Amounts in millions) 2025 2024 2023 Net cash used in investing activities $ (21,379) $ (21,287) $ (17,722) Net cash used in investing activities was $21.4 billion, $21.3 billion and $17.7 billion for fiscal 2025, 2024 and 2023, respectively, and generally consisted of capital expenditures. Net cash used in investing activities increased $0.1 billion for fiscal 2025 when compared to the previous fiscal year. The increase is primarily due to increased purchases of property and equipment as well as the acquisition of VIZIO for net consideration of $1.9 billion, partially offset by net proceeds received from sales of certain strategic investments, including $3.6 billion related to the sale of o

> [P5] (Amounts in millions) 2026 2025 2024 Net cash used in investing activities $ (26,350) $ (21,379) $ (21,287) Net cash used in investing activities generally consisted of capital expenditures. Net cash used in investing activities increased $5.0 billion for fiscal 2026 when compared to the previous fiscal year. The increase is primarily due to the change in net proceeds received from the sale of certain strategic investments as well as increased payments for property and equipment, partially offset by the acquisition of VIZIO for net consideration of $1.9 billion in the prior year. Net cash used in investing activities increased $0.1 billion for fiscal 2025, when compared to the previous fisca

judge: supported

verdict: [ ]

## claim-070  (baseline cross-183)

**Claim:** A reduction in net income contributed to the overall decline

> [P1] 2025 2024 Net income $ 5,572 $ 5,782 Non-cash operating activities(1) 5,169 5,622 Pension and postretirement medical benefit plan contributions (Company-sponsored plans) (1,361) (1,524) Hedge margin receivables and payables — (90) Income tax receivables and payables (330) 313 Changes in working capital and other non-current assets and liabilities (667) 33 Other operating activities 67 (14) Net cash from operating activities $ 8,450 $ 10,122 (1) Represents depreciation and amortization, gains and losses on derivative transactions and foreign currency exchange, disposals of assets and businesses, deferred income taxes, allowances for expected credit losses, amortization of operating lease asse

> [P2] 2025 2024 Net cash used in investing activities $ (4,735) $ (217) Capital Expenditures: Buildings, facilities and plant equipment $ (2,206) $ (1,563) Aircraft and parts (171) (742) Vehicles (245) (779) Information technology (1,063) (825) Total capital expenditures(1): $ (3,685) $ (3,909) Capital expenditures as a % of revenue 4.2 % 4.3 % Other Investing Activities: Proceeds from disposal of businesses, property, plant and equipment $ 700 $ 1,115 Net (purchases) sales and maturities of marketable securities $ 203 $ 2,672 Acquisitions, net of cash acquired $ (1,968) $ (71) Other investing activities $ 15 $ (24) (1) In addition to capital expenditures of $3.7 and $3.9 billion for 2025 and 2024

> [P3] As of December 31, 2025 approximately $2.0 billion of our total worldwide holdings of cash, cash equivalents and marketable securities were held by foreign subsidiaries. The amount of cash, cash equivalents and marketable securities held by our U.S. and foreign subsidiaries fluctuates throughout the year due to a variety of factors, including the timing of cash receipts, strategic operating needs and disbursements in the normal course of business. Cash provided by operating activities in the U.S. continues to be our primary source of funds to finance our business operations, planned capital expenditures, pension contributions, planned acquisitions, transformation strategy costs, debt obligat

> [P4] Cash paid for acquisitions in 2025 was primarily attributable to the acquisitions of Frigo-Trans, AHG and reacquired development area rights for The UPS Store. Cash paid for acquisitions in 2024 primarily related to reacquired development area rights for The UPS Store. In 2025, non-cash investing activities included construction-in-progress of $107 million related to the capitalization of construction costs in connection with a build-to-suit financing obligation. We have commitments for the purchase of equipment, real estate and vehicles to provide for the replacement and enhancement of existing capacity and targeted growth. It also provides for maintenance of buildings, facilities and equip

> [P5] We have no material off-balance sheet arrangements. CASH FLOWS SUMMARY Operating Activities Cash flow generated from operations provides us with a significant source of liquidity. Our operating cash flows result primarily from cash received from our customers, offset by cash payments we make for products and services, associate compensation, operations, occupancy costs, and income taxes. Cash provided by or used in operating activities is also subject to changes in working capital. Working capital at any point in time is subject to many variables, including seasonality, inventory management and category expansion, the timing of cash receipts and payments, vendor payment terms, and fluctuatio

judge: supported

verdict: [ ]

## claim-071  (agent cross-177)

**Claim:** Device Mix: Changes in device mix are a factor that influences cost-per-click and cost-per-impression, which in turn affect advertising revenues

> [P1] Google Search & other $ 198,084 $ 224,532 YouTube ads 36,147 40,367 Google Network 30,359 29,792 Google advertising 264,590 294,691 Google subscriptions, platforms, and devices 40,340 48,030 Google Services total 304,930 342,721 Google Cloud 43,229 58,705 Other Bets 1,648 1,537 Hedging gains (losses) 211 (127) Total revenues $ 350,018 $ 402,836 Google Services Google Advertising Google Search & other Google Search & other revenues increased $26.4 billion from 2024 to 2025. The overall growth was driven by interrelated factors including increases in search queries resulting from growth in user adoption and usage on mobile devices; growth in advertiser spending; and improvements we have made i

> [P2] Impressions include impressions displayed to users on Google Network properties participating primarily in AdMob, AdSense, and Google Ad Manager. Cost-per-impression is defined as impression-based and click-based revenues divided by our total number of impressions, and represents the average amount we charge advertisers for each impression displayed to users. As our business evolves, we periodically review, refine, and update our methodologies for monitoring, gathering, and counting the number of paid clicks and the number of impressions, and for identifying the revenues generated by the corresponding click and impression activity. Fluctuations in our advertising revenues, as well as the cha

> [P3] Impressions change (7) % Cost-per-impression change 7 % Changes in paid clicks and impressions are driven by a number of interrelated factors, including changes in advertiser spending; ongoing product and policy changes; and, as it relates to paid clicks, fluctuations in search queries resulting from changes in user adoption and usage, primarily on mobile devices. Changes in cost-per-click and cost-per-impression are driven by a number of interrelated factors including changes in device mix, geographic mix, advertiser spending, ongoing product and policy changes, product mix, property mix, and changes in foreign currency exchange rates. Google Subscriptions, Platforms, and Devices Google sub

> [P4] Our revenue growth rate could decline over time, and we may experience downward pressure on our operating margin in the future. Our revenue growth rate could decline over time as a result of a number of factors, including changes in the devices and modalities used to access our products and services; changes in geographic mix; deceleration or declines in advertiser spending; competition; changes in customer usage and demand for our existing products and increasing demand for new technologies; decreases in the pricing of our products and services; ongoing product and policy changes; and shifts to lower priced products and services. In addition, we may experience downward pressure on our opera

> [P5] Our users are accessing our products and services via diverse devices and modalities beyond traditional desktop, such as smartphones, wearables, connected TVs, and smart home devices, and want to be able to be connected no matter where they are or what they are doing. We are focused on expanding our products and services to stay in front of these trends in order to maintain and grow our business. We benefit from advertising revenues generated from different channels, including mobile, and newer advertising formats. The margins from these channels and newer products have generally been lower than those from traditional desktop search. Additionally, as the market for a particular device type o

> [P6] Impressions change (11) % Cost-per-impression change 10 % Changes in paid clicks and impressions are driven by a number of interrelated factors, including changes in advertiser spending; ongoing product and policy changes; and, as it relates to paid clicks, fluctuations in search queries resulting from changes in user adoption and usage, primarily on mobile devices. Changes in cost-per-click and cost-per-impression are driven by a number of interrelated factors including changes in device mix, geographic mix, advertiser spending, ongoing product and policy changes, product mix, property mix, and changes in foreign currency exchange rates.

> [F1] ticker = GOOGL, fiscal_year = 2024, metric = revenue, value = 350018000000.0

judge: supported

verdict: [ ]

## claim-072  (agent sql-063)

**Claim:** Pfizer's total liabilities for fiscal year 2022 were $101.29 billion

> [F1] ticker = PFE, fiscal_year = 2022, metric = total_liabilities, value = 101288000000.0

judge: supported

verdict: [ ]

## claim-073  (baseline text-099)

**Claim:** The actual cost or severity of claims can be influenced by trends in healthcare and litigation costs.

> [P1] Insurance and claims expense could materially adversely affect us. We have a combination of both self-insurance and high-deductible insurance programs for the risks arising out of our business and operations, including claims exposure resulting from cargo loss, cyber-attacks, personal injury, property damage, aircraft and related liabilities, business interruption and workers' compensation. Self-insured workers' compensation, automobile and general liabilities are determined using actuarial estimates of the aggregate liability for claims incurred and an estimate of incurred but not reported claims, on an undiscounted basis. Our accruals for insurance reserves reflect certain actuarial assump

> [P2] Insurance and claims expense could materially adversely affect us. We have a combination of both self-insurance and high-deductible insurance programs for the risks arising out of our business and operations, including claims exposure resulting from cargo loss, cyber-attacks, personal injury, property damage, aircraft and related liabilities, business interruption and workers' compensation. Self-insured workers' compensation, automobile and general liabilities are determined using actuarial estimates of the aggregate liability for claims incurred and an estimate of incurred but not reported claims, on an undiscounted basis. Our accruals for insurance reserves reflect certain actuarial assump

> [P3] Workers' compensation, automobile liability and general liability insurance claims may take a number of years to resolve. Consequently, actuarial estimates are required to project the ultimate cost that will be incurred to resolve a claim. Several factors can affect the actual cost, or severity, of a claim, including: •Risk retention limits; •Length of time a claim remains open; •Trends in healthcare and litigation costs; •Results of any related litigation; and •Changes in legislation. UNITED PARCEL SERVICE, INC. AND SUBSIDIARIES MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS Furthermore, claims may emerge in future years for events that occurred in a p

> [P4] Our finite-lived intangible assets are amortized over their estimated useful lives. These assets are tested for impairment as part of asset groups that may include other long-lived assets. See "Critical Accounting Estimates – Depreciation, Residual Value and Impairment of Property, Plant and Equipment" for a discussion of estimates impacting asset groups. In addition, a reduction in expected useful life, or a decision to sell or abandon an intangible asset before the end of its useful life, may increase amortization expense, which could have a material impact on our results of operations. UNITED PARCEL SERVICE, INC. AND SUBSIDIARIES MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION

> [P5] We are predominantly self-insured for a number of different risk categories, such as general liability (including product liability), property loss, workers’ compensation, employee group medical, employment practices liability and wage and hour claims, automobile claims, and cybersecurity and privacy liability, with insurance coverage for certain catastrophic risks above the self-insurance levels. The types and amounts of insurance may vary from time to time based on our decisions with respect to risk retention and regulatory requirements. The occurrence of significant claims, a substantial rise in costs to maintain our insurance, the failure to maintain adequate insurance coverage, or dispu

judge: supported

verdict: [ ]

## claim-074  (baseline text-107)

**Claim:** Apple employs encryption, authentication technologies, and multifactor authentication to protect against unauthorized access

> [P1] The Company has implemented systems and processes intended to secure its information technology systems and prevent unauthorized access to or loss of sensitive data, and mitigate the impact of unauthorized access, including through the use of encryption and authentication technologies. As with all companies, these security measures may not be sufficient for all eventualities and are vulnerable to hacking, ransomware attacks, employee error, malfeasance, system error, faulty password management or other irregularities. For example, third parties can fraudulently induce the Company’s or its suppliers’ and other third parties’ employees or customers into disclosing usernames, passwords or other

> [P2] As with all companies, the security the Company has implemented may not be sufficient for all eventualities and are vulnerable to hacking, ransomware attacks, employee error, malfeasance, system error, faulty password management or other irregularities. For example, third parties can fraudulently induce the Company’s or its suppliers’ and other third parties’ employees or customers into disclosing usernames, passwords or other sensitive information, which can, in turn, be used for unauthorized access to the Company’s or such suppliers’ or third parties’ systems and services. To help protect customers and the Company, the Company deploys and makes available technologies like multifactor authe

> [P3] The Company’s business and reputation are impacted by information technology system failures and network disruptions. The Company and its global supply chain are dependent on complex information technology systems and are exposed to information technology system failures or network disruptions caused by natural disasters, accidents, power disruptions, telecommunications failures, acts of terrorism or war, computer viruses, physical or electronic break-ins, ransomware or other cybersecurity incidents, or other events or disruptions. System upgrades, redundancy and other continuity measures may be ineffective or inadequate, and the Company’s or its vendors’ business continuity and disaster rec

> [P4] The Company’s business and reputation are impacted by information technology system failures and network disruptions. The Company and its global supply chain are dependent on complex information technology systems and are exposed to information technology system failures or network disruptions caused by natural disasters, accidents, power disruptions, telecommunications failures, acts of terrorism or war, computer viruses, physical or electronic break-ins, ransomware or other cybersecurity incidents, or other events or disruptions. System upgrades, redundancy and other continuity measures may be ineffective or inadequate, and the Company’s or its vendors’ business continuity and disaster rec

> [P5] The Company’s global operations are subject to complex and changing laws and regulations worldwide on subjects including antitrust; privacy, data security and data localization; online safety; age verification; consumer protection; advertising, sales, billing and e-commerce; financial services and technology; product liability; intellectual property ownership and infringement; digital platforms; machine learning and artificial intelligence; internet, telecommunications and mobile communications; media, television, film and digital content; availability of third-party software applications and services; labor and employment; anticorruption; import, export and trade; foreign exchange controls

judge: supported

verdict: [ ]

## claim-075  (baseline text-150)

**Claim:** The Tahiti Field has an estimated remaining production life of more than 15 years.

> [P1] Chevron has a 58 percent-owned and operated interest in the deepwater Tahiti Field, located in the Green Canyon area. In 2025, a development well workover was executed to deliver first oil from a shallower reservoir as water injection operations continued. The Tahiti Field has an estimated remaining production life of more than 15 years. Chevron has a 42.5 percent nonoperated working interest in Green Canyon Block 584. In 2025, the operator announced an oil discovery at the Far South prospect in this Block, with an initial well and sidetrack drilled to a total depth of 23,830 feet. Chevron has a 15.6 percent nonoperated working interest in the deepwater Mad Dog Field, located in the Green Ca

> [P2] California Chevron owns and operates between 87 and 100 percent interests in six fields in California including Kern River, Cymric/McKittrick, Midway Sunset, San Ardo, Coalinga and Lost Hills. In 2025, Chevron’s California average net Table of Contents daily oil-equivalent production was 63,000 barrels. Following Kern County’s reinstatement of drilling permit approvals, Chevron plans to undertake limited development drilling in 2026. Gulf of America Chevron is the largest acreage holder in the Gulf of America, following its acquisition of Hess. During 2025, Chevron’s net daily production in the Gulf of America averaged 235,000 barrels of crude oil, 19,000 barrels of NGLs and 150 million cubi

> [P3] Chevron has a 41.5 percent nonoperated working interest in the deepwater Whale Field located in the Alaminos Canyon area. Whale consists of a 15-well subsea development and floating production unit. First production was achieved in January 2025, and nameplate capacity was reached in September as eight wells were brought online throughout the year. The field has an estimated remaining production life of more than 25 years. In addition to Stampede, Chevron acquired further assets in the Gulf of America from Hess, including a 100 percent-owned and operated interest in the Pickerel Field, a 50 percent-owned and operated interest in the Baldpate and Penn State fields, a 38 percent-owned and opera

> [P4] Chevron has a 62.9 percent-owned and operated interest in the unit areas containing the Anchor Field, located in the Green Canyon area. Stage 1 of the Anchor development that consists of a seven-well subsea development and a semi-submersible floating production unit achieved first oil in August 2024 utilizing an industry-first 20,000 pounds per square inch Table of Contents deepwater technology. Two producing wells were brought online and development drilling is progressing on subsequent wells. The field has an estimated remaining production life of 30 years. Chevron has a 60 percent-owned and operated interest in the Ballymore Field located in the Mississippi Canyon area, which is being dev

> [P5] Chevron has a 50 percent-owned and operated interest in the Jack Field, a 51 percent-owned and operated interest in the St. Malo Field and a 40.6 percent-owned and operated interest in the production host facility used for the joint development of both fields, all located in the Walker Ridge area. In 2024, the St. Malo Stage 4 waterflood project delivered first water injection and completed the installation of a second multi-phase subsea pump module within the St. Malo Field. An additional St. Malo well delivered first oil and further development drilling commenced in the Jack Field. The Jack/St. Malo Stage 5 project reached final investment decision (FID), with first oil expected in 2026. T

judge: supported

verdict: [ ]

## claim-076  (baseline cross-194)

**Claim:** The $3.5 billion decrease in net cash provided by operating activities in fiscal 2025 was primarily driven by the timing of vendor payments and increased inventories.

> [P1] We have no material off-balance sheet arrangements. CASH FLOWS SUMMARY Operating Activities Cash flow generated from operations provides us with a significant source of liquidity. Our operating cash flows result primarily from cash received from our customers, offset by cash payments we make for products and services, associate compensation, operations, occupancy costs, and income taxes. Cash provided by or used in operating activities is also subject to changes in working capital. Working capital at any point in time is subject to many variables, including seasonality, inventory management and category expansion, the timing of cash receipts and payments, vendor payment terms, and fluctuatio

> [P2] We reported net sales of $164.7 billion in fiscal 2025. Net earnings were $14.2 billion, or $14.23 per diluted share. During fiscal 2025, we generated $16.3 billion of cash flow from operations, received $4.1 billion of proceeds from commercial paper borrowings, net of repayments, and received $2.2 billion of proceeds from the issuance of long-term debt, net of discounts. This cash flow, together with cash on hand, was used to fund $9.2 billion in cash dividends, repay $5.0 billion of long-term debt, and fund $3.7 billion in capital expenditures. As described below, we also completed the GMS acquisition for aggregate cash consideration totaling approximately $5.5 billion, including the repay

> [P3] During fiscal 2024, we invested approximately $3.5 billion back into our business in the form of capital expenditures. In line with our expectation of approximately 2.5% of fiscal 2025 net sales, we plan to invest approximately $4 billion back into our business in the form of capital expenditures in fiscal 2025, with investments across initiatives to improve the customer experience, including through technology and development of other differentiated capabilities, to continue to mature and build out Pro capabilities, as well as to build new stores. However, we may adjust our capital expenditures to support the operations of the business, to enhance long-term strategic positioning, or in resp

> [P4] Backlog BGS total backlog of $29,720 million at December 31, 2025 increased by 39% from $21,403 million at December 31, 2024, primarily due to the timing of awards, partially offset by revenue recognized on contracts awarded in prior years. Table of Contents Liquidity and Capital Resources Cash Flow Summary (Dollars in millions) Years ended December 31, 2025 2024 2023 Net earnings/(loss) $2,238 ($11,829) ($2,242) Non-cash items (171) 8,517 4,113 Changes in assets and liabilities (1,002) (8,768) 4,089 Net cash provided/(used) by operating activities 1,065 (12,080) 5,960 Net cash provided/(used) by investing activities 499 (11,973) (2,437) Net cash (used)/provided by financing activities (3,76

> [P5] Cash flow generated from operations provides us with a significant source of liquidity. Our operating cash flows result primarily from cash received from our customers, offset by cash payments we make for products and services, associate compensation, operations, occupancy costs, and income taxes. Cash provided by or used in operating activities is also subject to changes in working capital. Working capital at any point in time is subject to many variables, including seasonality, inventory management and category expansion, the timing of cash receipts and payments, vendor payment terms, and fluctuations in foreign exchange rates. Net cash provided by operating activities decreased by $1.4 bi

judge: supported

verdict: [ ]

## claim-077  (baseline text-083)

**Claim:** At the end of fiscal year 2025, the total amount of nonperforming consumer loans, leases, and foreclosed properties for Bank of America was $2,666 million.

> [P1] Other Consumer Other consumer primarily consists of deposit overdraft balances. Net charge-offs decreased $57 million in 2025 to $238 million, primarily driven by lower overdraft losses. Nonperforming Consumer Loans, Leases and Foreclosed Properties Activity Table 28 presents nonperforming consumer loans, leases and foreclosed properties activity during 2025 and 2024. During 2025, nonperforming consumer loans of $2.6 billion decreased $71 million. At December 31, 2025, $450 million, or 17 percent, of nonperforming loans were 180 days or more past due and had been written down to their estimated property value less costs to sell. In addition, at December 31, 2025, $1.5 billion, or 58 percent,

> [P2] Total outstanding commercial real estate loans $ 68,748 $ 65,730 By Property Type Non-residential Industrial / Warehouse $ 13,031 $ 13,166 Office 12,447 15,061 Multi-family rental 10,986 11,022 Shopping centers / Retail 6,947 5,603 Hotel / Motels 4,629 4,680 Multi-use 2,509 2,162 Other 17,295 13,179 Total non-residential 67,844 64,873 Residential 904 857 Total outstanding commercial real estate loans $ 68,748 $ 65,730 U.S. Small Business Commercial The U.S. small business commercial loan portfolio is comprised of small business card loans and small business loans primarily managed in Consumer Banking. Credit card-related products were 51 percent and 53 percent of the U.S. small business comm

> [P3] Table 34 Nonperforming Commercial Loans, Leases and Foreclosed Properties Activity (1, 2) (Dollars in millions) 2025 2024 Nonperforming loans and leases, beginning of period $ 3,328 $ 2,773 Additions 3,182 3,914 Reductions: Paydowns (1,852) (1,669) Sales (156) (32) Returns to performing status (3) (245) (182) Charge-offs (1,029) (1,361) Transfers to foreclosed properties — (115) Total net (reductions) additions to nonperforming loans and leases (100) 555 Total nonperforming loans and leases, December 31 3,228 3,328 Foreclosed properties, December 31 11 56 Nonperforming commercial loans, leases and foreclosed properties, December 31 $ 3,239 $ 3,384 Nonperforming commercial loans and leases as

> [P4] Nonperforming consumer loans and leases as a percentage of outstanding consumer loans and leases (3) 0.53 % 0.58 % Nonperforming consumer loans, leases and foreclosed properties as a percentage of outstanding consumer loans, leases and foreclosed properties (3) 0.55 0.60 (1)Consumer loans may be returned to performing status when all principal and interest is current and full repayment of the remaining contractual principal and interest is expected, or when the loan otherwise becomes well-secured and is in the process of collection. (2)Includes repossessed non-real estate assets of $31 million and $29 million at December 31, 2025 and 2024. (3)Outstanding consumer loans and leases exclude loa

> [P5] During 2025, the U.S. unemployment rate and home prices remained relatively stable. Net charge-offs decreased $90 59 Bank of America million to $4.1 billion in 2025, primarily driven by the other consumer and credit card portfolios. The consumer allowance for loan and lease losses decreased $190 million to $8.4 billion from 2024. For more information, see Allowance for Credit Losses on page 73. For more information on our accounting policies regarding delinquencies, nonperforming status, charge-offs and loan modifications for the consumer portfolio, see Note 1 – Summary of Significant Accounting Principles and Note 5 – Outstanding Loans and Leases and Allowance for Credit Losses to the Conso

judge: supported

verdict: [ ]

## claim-078  (baseline adversarial-007)

**Claim:** Total dealer inventory increased by approximately $400 million in 2024

> [P1] In the first quarter of 2026 as compared to the first quarter of 2025, we expect stronger sales and revenues primarily due to higher sales volume and favorable price realization. We expect higher sales volume to be mainly driven by higher sales of equipment to end users and by the impact from changes in machine dealer inventories. We expect machine dealer inventory to increase in excess of $1.0 billion during the first quarter of 2026, aligning with the seasonal pattern, compared to roughly flat levels in the first quarter of 2025. In the first quarter of 2026 as compared to the first quarter of 2025, we anticipate strong sales growth in Construction Industries, primarily due to higher sales

> [P2] North America sales decreased 1 percent primarily due to lower sales volume, partially offset by favorable price realization. The decrease in sales volume was mainly due to the impact from changes in dealer inventories. Dealer inventory increased less during 2024 than during 2023. Sales increased 1 percent in Latin America. Unfavorable currency impacts related to the Brazilian real were more than offset by higher sales volume and favorable price realization. The increase in sales volume was primarily due to the impact from changes in dealer inventories. Dealer inventory increased during 2024, compared to a decrease during 2023. EAME sales decreased 10 percent primarily due lower sales volume

> [P3] We continue to monitor a variety of external factors around the world, such as supply chain disruptions, inflationary cost and labor pressures. Areas of particular focus include transportation, certain components and raw materials. We continue to work to minimize supply chain challenges that may impact our ability to meet customer demand. We continue to assess the environment to determine if additional actions need to be taken. Risk Factors Risk factors are disclosed within Item 1A. Risk Factors of the 2024 Form 10-K. Notes: •Glossary of terms included on pages 35 - 37; first occurrence of terms shown in bold italics. •Information on non-GAAP financial measures is included on pages 47 - 48.

> [P4] EAME sales increased 4 percent mainly due to higher sales volume and favorable currency impacts related to the euro, partially offset by unfavorable price realization. The increase in sales volume was primarily driven by the impact from changes in dealer inventories. Dealer inventory increased in 2025, compared to a decrease in 2024. Asia/Pacific sales decreased 2 percent primarily due to unfavorable currency impacts related to the Australian dollar, and lower sales volume. The decrease in sales volume was mainly driven by lower sales of equipment to end users. Total dealer inventory increased about $900 million during 2025, compared to an increase of about $400 million during 2024. Machine

> [P5] We sell finished products primarily through an independent dealer network and directly to OEMs and are subject to risks relating to their inventory management decisions and operational and sourcing practices. Both carry inventories of finished products as part of ongoing operations and adjust those inventories based on their assessments of future needs and market conditions, including levels of used equipment inventory and machine rental usage rates. Such adjustments may impact our results positively or negatively. If the inventory levels of our dealers and OEM customers are higher than they desire, they may postpone product purchases from us, which could cause our sales to be lower than the

judge: supported

verdict: [ ]

## claim-079  (agent text-156)

**Claim:** This was driven by new wells online in the Delaware Basin, Eagle Ford, Bakken, and Midland Basin, and the acquisition of Marathon Oil

> [P1] Millions of Dollars Years Ended December 31 2025 2024 2023 Sales and other operating revenues $ 58,944 54,745 56,141 Equity in earnings of affiliates 1,335 1,705 1,720 Gain (loss) on dispositions 731 51 228 Purchased commodities 22,325 20,012 21,975 Production and operating expenses 10,331 8,751 7,693 Selling, general and administrative expenses 893 1,158 705 Depreciation, depletion and amortization 11,500 9,599 8,270 Other expenses 20 181 2 Income tax provision (benefit) 4,668 4,427 5,331 Sales and other operating revenues increased $4,199 million in 2025, primarily due to higher volumes of $6,197 million, inclusive of sales volumes from our acquisition of Marathon Oil and higher realized g

> [P2] Net Income (Loss) Lower 48 reported earnings of $5,264 million in 2025, compared with earnings of $5,175 million in 2024. Increases to earnings included higher revenues resulting from higher volumes of $3,890 million, inclusive of volumes from our acquisition of Marathon Oil, partly offset by lower commodity prices of $1,999 million, driven by lower crude prices. Additional increases included higher gains on dispositions of $494 million, primarily associated with the divestitures of the Ursa and Europa fields and Ursa Oil Pipeline Company LLC, and other noncore assets. Decreases to earnings included higher DD&A of $1,330 million and higher production and operating expenses of $875 million, p

> [P3] Net Income (Loss) The Europe, Middle East and North Africa segment reported earnings of $1,224 million in 2025 compared with earnings of $1,189 million in 2024. Earnings in 2025 included higher revenues resulting from higher volumes of $296 million, including volumes from our Equatorial Guinea assets from the acquisition of Marathon Oil, partly offset by lower overall realized commodity prices of $185 million, driven by lower crude prices. See Note 3. Decreases to earnings included higher production and operating expenses of $88 million, primarily from our acquisition of Marathon Oil. See Note 3. Consolidated Production Average consolidated production increased 40 MBOED in 2025, compared wit

> [P4] Crude and bitumen prices were lower through 2025 as global oil supplies increased faster than global oil demand. Natural gas prices increased due to stronger demand and lower inventory levels relative to 2024. Our worldwide annual average realized price decrease was driven by lower crude and bitumen prices. ConocoPhillips 2025 10-K Management’s Discussion and Analysis Table of Contents Key Operating and Financial Summary Significant items during 2025 and recent announcements included the following: •Reported fourth-quarter 2025 earnings per share of $1.17; •Generated cash provided by operating activities of $19.8 billion; •Distributed $9.0 billion to shareholders, including $5.0 billion thro

> [P5] At December 31, 2025, we had cash and cash equivalents of $6.5 billion, short-term investments of $0.5 billion, and available borrowing capacity under our credit facility of $5.5 billion, totaling approximately $12.5 billion of liquidity. In addition, we have long-term investments in debt securities of $1.1 billion. We believe current cash balances and cash generated by operations, together with access to external sources of funds as described below in the “Significant Changes in Capital” section, will be sufficient to meet our funding requirements in the near- and long-term, including our capital spending program, capital return program and required debt payments. Significant Changes in Cap

> [P6] Net Income (Loss) Asia Pacific reported earnings of $1,167 million in 2025, compared with $1,724 million in 2024. Decreases to earnings included lower revenues resulting from lower commodity prices of $206 million. Additional decreases to earnings included lower earnings from equity affiliates of $271 million, primarily due to lower LNG sales prices and higher exploration expenses of $64 million, primarily driven by dry hole expenses associated with certain wells in Malaysia and Australia. Consolidated Production Average consolidated production increased three MBOED in 2025, compared with 2024. Increases to production were primarily due to development activity in Bohai Bay in China and Gumus

judge: supported

verdict: [ ]

## claim-080  (baseline text-146)

**Claim:** The EU AI Act may impact the company's ability to train, deploy, or release AI models in the EU.

> [P1] If we enable or offer solutions that draw controversy due to their perceived or actual impact on society, such as AI solutions that have unintended consequences, infringe copyright or rights of publicity, or are controversial because of their impact on human rights, privacy, employment or other social, economic or political issues, or if we are unable to develop effective internal policies and frameworks relating to the responsible development and use of AI models and systems offered through our sales channels, we may experience brand or reputational harm, competitive harm or legal liability. Leveraging AI capabilities to potentially improve our internal functions and operations may present

> [P2] Compliance with laws, rules, and regulations has not otherwise had a material effect upon our capital expenditures, results of operations, or competitive position and we do not currently anticipate material capital expenditures for environmental control facilities. Compliance with existing or future governmental regulations, including, but not limited to, those pertaining to IP ownership and infringement, taxes, import and export requirements and tariffs, anti-corruption, business acquisitions, foreign exchange controls and cash repatriation restrictions, data privacy requirements, competition and antitrust, advertising, employment, product regulations, cybersecurity, environmental, health a

> [P3] On January 15, 2025, the USG published the “AI Diffusion” IFR in the Federal Register. After a 120-day delayed compliance period, the IFR will, unless modified, impose a worldwide licensing requirement on all products classified under Export Control Classification Numbers, or ECCNs, 3A090.a, 4A090.a, or corresponding .z ECCNs, including all related software and technology. Any system that incorporates one or more of the covered integrated circuits, or ICs, (including but not limited to NVIDIA DGX, HGX, and MGX systems) will be covered by the new licensing requirement. The licensing requirement will include future NVIDIA ICs, boards, or systems classified with ECCN 3A090.a or 4A090.a, or corr

> [P4] Governments and regulators are also considering, and in certain cases, have imposed restrictions on the hardware, software, and systems used to develop frontier foundation models and generative AI. For example, the EU AI Act became effective on August 1, 2024 and will be fully applicable after a two-year transitional period. The EU AI Act may impact our ability to train, deploy, or release AI models in the EU. Several states are considering enacting or have already enacted regulations concerning AI technologies, which may impact our ability to train, deploy, or release AI models, and increase our compliance costs. Restrictions under these and any other regulations, if implemented, could incr

> [P5] Certain shareholder advocacy groups, investment funds, shareholders and other market participants, customers and government regulators have focused on corporate sustainability practices and disclosures, including those associated with climate change and human rights. Stakeholders may not be satisfied with our corporate sustainability practices and goals or the speed of their adoption. Further, there are state-level initiatives in the U.S. that may differ from other regulatory requirements or our various stakeholders’ expectations. Additionally, our corporate sustainability practices, oversight of our practices or disclosure controls may not meet evolving shareholder, regulator or other indus

judge: supported

verdict: [ ]

## claim-081  (agent sql-052)

**Claim:** Costco's operating income for fiscal year 2025 was $10.38 billion

> [F1] ticker = COST, fiscal_year = 2025, metric = operating_income, value = 10383000000.0

judge: supported

verdict: [ ]

## claim-082  (baseline text-148)

**Claim:** Growth was partially offset by a decrease in the number of people served through risk-based commercial offerings

> [P1] South American businesses held for sale 1,160 1,330 5,540 (170) (13) % UnitedHealthcare’s revenues increased due to the IRA-driven impacts on Medicare Part D plans and growth in the number of people served through Medicare Advantage, fee-based commercial offerings, those with higher acuity needs and Medicaid rates, partially offset by a decrease in people served through risk-based commercial offerings and Medicaid offerings. Earnings from operations decreased primarily due to the impacts of Medicare Advantage funding reductions, elevated medical cost trend, gains related to business portfolio refinement in 2024, the impacts of market morbidity changes on our individual exchange offerings, ot

> [P2] SELECTED OPERATING PERFORMANCE ITEMS The following summarizes select 2025 year-over-year operating comparisons to 2024 and other financial results. •Consolidated revenues grew 12%, UnitedHealthcare revenues grew 16% and Optum revenues grew 7%. •UnitedHealthcare served 415,000 more people domestically, driven by growth in fee-based commercial offerings and Medicare Advantage, partially offset by risk-based commercial offerings. •Earnings from operations of $19.0 billion compared to $32.3 billion last year, impacted by elevated medical cost trend, restructuring and other actions, gains related to business portfolio refinement in 2024, partially offset by net portfolio divestitures in 2025 and

> [P3] Worldwide sales were $65.0 billion in 2025, representing growth of 1% compared with 2024, or 2% excluding the unfavorable effect of foreign exchange. Global sales growth was primarily due to higher sales in the oncology franchise, largely due to the performance of Keytruda and Welireg, as well as increased alliance revenue from Koselugo (resulting from an amendment to the collaboration agreement), Reblozyl, and Lynparza. Also contributing to revenue growth in 2025 were higher sales in the cardiometabolic and respiratory franchise, largely attributable to the ongoing launch of Winrevair, as well as the inclusion of Ohtuvayre sales following the October 2025 acquisition of Verona Pharma. Growt

> [P4] For the Years Ended December 31, Change (in millions, except percentages) 2025 2024 2023 2025 vs. 2024 Revenues UnitedHealthcare $ 344,903 $ 298,208 $ 281,360 $ 46,695 16 % Optum Health 101,957 105,358 95,319 (3,401) (3) Optum Insight 19,417 18,757 18,932 660 4 Optum Rx 154,726 133,231 116,087 21,495 16 Optum eliminations (5,480) (4,389) (3,703) (1,091) 25 Optum 270,620 252,957 226,635 17,663 7 Eliminations (167,956) (150,887) (136,373) (17,069) 11 Consolidated revenues $ 447,567 $ 400,278 $ 371,622 $ 47,289 12 % Earnings from operations UnitedHealthcare $ 9,425 $ 15,584 $ 16,415 $ (6,159) (40) % Optum Health (278) 7,770 6,560 (8,048) (104) Optum Insight 2,624 3,097 4,268 (473) (15) Optum Rx

> [P5] Direct Response Costs – Cyberattack To support care providers impacted by the Change Healthcare cyberattack that occurred on February 21, 2024, the Company provided interest-free loans. In the fourth quarter of 2025, the Company increased its reserves for net collection expectations associated with provider loans and other customer balances of $799 million, which were recorded within operating costs on the Consolidated Statements of Operations and related to Optum Insight. Business Trends Our businesses participate primarily in the United States health markets. In the United States, health care spending has grown consistently for many years and accounted for 19% of gross domestic product (GD

judge: supported

verdict: [ ]

## claim-083  (baseline text-088)

**Claim:** Keytruda is approved as monotherapy for the adjuvant treatment of certain patients with melanoma

> [P1] Pharmaceutical The Pharmaceutical segment includes human health pharmaceutical and vaccine products. Human health pharmaceutical products consist of therapeutic and preventive agents, generally sold by prescription, for the treatment of human disorders. Human health vaccine products consist of preventive pediatric, adolescent and adult vaccines. Certain of the products within the Company’s franchises are as follows: Table of Contents Oncology Keytruda is an anti-PD-1 (programmed death receptor-1) therapy that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroeso

> [P2] The Company received more than 25 regulatory approvals in major markets in 2024, including the Winrevair and Capvaxive approvals noted above, along with numerous approvals in oncology. Keytruda received approval for additional indications in the U.S. and/or internationally as monotherapy in the therapeutic areas of hepatocellular carcinoma (HCC), melanoma and urothelial carcinoma, in combination with chemotherapy in the therapeutic areas of biliary tract cancer, cervical cancer, endometrial carcinoma, gastric or gastroesophageal junction (GEJ) adenocarcinoma, malignant pleural mesothelioma and non-small-cell lung cancer (NSCLC), as well as in combination with Padcev (enfortunab vedotin-ejfv)

> [P3] MK-3475, Keytruda, is an anti-PD-1 therapy approved for the treatment of many cancers that is in clinical development for expanded indications. These studies encompass more than 30 cancer types including: biliary, estrogen receptor positive breast, triple-negative breast, cervical, colorectal, endometrial, esophageal, gastric, glioblastoma, head and neck, hepatocellular, Hodgkin lymphoma, non-Hodgkin lymphoma, non-small-cell lung, small-cell lung, melanoma, malignant pleural mesothelioma, ovarian, prostate, renal, and urothelial, several of which are currently in Phase 3 clinical development. Further trials are being planned for other cancers. Keytruda is under review in the EU and Japan for

> [P4] Keytruda (pembrolizumab) is an anti-PD-1 (programmed death receptor-1) therapy available for intravenous administration that has been approved as monotherapy for the treatment of certain patients with cervical cancer, classical Hodgkin lymphoma (cHL), cutaneous squamous cell carcinoma, esophageal or gastroesophageal junction (GEJ) carcinoma, head and neck squamous cell carcinoma (HNSCC), hepatocellular carcinoma (HCC), melanoma, Merkel cell carcinoma, microsatellite instability-high (MSI-H) or mismatch repair deficient (dMMR) solid tumors (including MSI-H/dMMR colorectal cancer and endometrial carcinoma), non-small cell lung cancer (NSCLC), primary mediastinal large B-cell lymphoma (PMBCL),

> [P5] Disease (JPN) Pneumococcal Vaccine Adult V116 Capvaxive (EU) (JPN) Pulmonary Arterial Hypertension MK-7962 Winrevair (JPN) Respiratory Syncytial Virus MK-1654 (clesrovimab) (U.S.) (EU) Certain Supplemental Filings Cancer MK-3475 Keytruda • First-Line Unresectable Advanced or Metastatic Malignant Pleural Mesothelioma (KEYNOTE-483) (EU) (JPN) MK-6482 Welireg • Advanced, Unresectable, or Metastatic Pheochromocytoma and Paraganglioma (LITESPARK-015) (U.S.) Footnotes: (1) Being developed in a collaboration. (2) Being developed in combination with Keytruda. (3) Being developed as monotherapy and/or in combination with Keytruda. (4) FDA lifted clinical hold on December 4, 2024. (5) On FDA partial c

judge: supported

verdict: [ ]

## claim-084  (baseline cross-191)

**Claim:** In 2025, cash used in operating activities resulted from higher trading assets.

> [P1] Net cash provided by/ (used in) Operating activities $ (147,782) $ (42,012) $ 12,974 Investing activities (265,565) (163,403) 67,643 Financing activities 269,533 63,447 (25,571) Effect of exchange rate changes on cash 17,835 (12,866) 1,871 Net increase/(decrease) in cash and due from banks and deposits with banks $ (125,979) $ (154,834) $ 56,917 Operating activities JPMorganChase’s operating assets and liabilities primarily support the Firm’s lending and capital markets activities. These assets and liabilities can vary significantly in the normal course of business due to the amount and timing of cash flows, which are affected by client-driven and risk management activities and market condit

> [P2] December 31, 2024 (in millions, except ratios) 1 year or less After 1 year through 5 years After 5 years Total Investment-grade Noninvestment-grade Total Total % of IG Loans retained $ 225,982 $ 289,199 $ 175,215 $ 690,396 $ 471,670 $ 218,726 $ 690,396 68 % Derivative receivables 60,967 60,967 Less: Liquid securities and other cash collateral held against derivatives (28,160) (28,160) Total derivative receivables, net of collateral 11,515 7,418 13,874 32,807 24,707 8,100 32,807 75 Lending-related commitments 121,283 384,529 25,655 531,467 352,082 179,385 531,467 66 Subtotal 358,780 681,146 214,744 1,254,670 848,459 406,211 1,254,670 68 Loans held-for-sale and loans at fair value(a) 31,922 31

> [P3] Selected balance sheet data (period-end) Total assets $ 2,142,534 $ 1,773,194 $ 1,638,493 Loans: Loans retained 558,528 483,043 475,186 Loans held-for-sale and loans at fair value(a) 73,508 40,324 39,464 Total loans 632,036 523,367 514,650 Equity 149,500 132,000 138,000 Banking & Payments loans by client coverage segment (period-end)(b) Global Corporate Banking & Global Investment Banking(c) $ 146,079 (e) $ 125,270 $ 128,623 Commercial Banking 222,139 217,674 221,550 Commercial & Specialized Industries(d) 75,865 72,814 78,043 Commercial Real Estate Banking 146,274 144,860 143,507 Total Banking & Payments loans 368,218 342,944 350,173 Selected balance sheet data (average) Total assets $ 2,195

> [P4] •Interest rate risk and prepayment risk •Trading assets/liabilities-debt and marketable equity instruments, and derivatives, including hedges of the retained loan portfolio •Certain securities purchased, loaned or sold under resale agreements and securities borrowed •Fair value option elected liabilities(a) •Certain fair value option elected loans •Derivative CVA and associated hedges •Marketable equity investments •Retained and held-for-sale loan portfolios •Deposits •Privately held equity and other investments measured at fair value; and certain real estate-related fair value option elected loans •Derivatives FVA and fair value option elected liabilities DVA(a) AWM •Provides initial capita

> [P5] Refer to Note 12 for further information about this portfolio, including information about delinquencies, geographic and FICO composition. JPMorgan Chase & Co./2025 Form 10-K Management’s discussion and analysis WHOLESALE CREDIT PORTFOLIO In its wholesale businesses, the Firm is exposed to credit risk primarily through its underwriting, lending, market-making, and hedging activities with and for clients and counterparties, as well as through various operating services (such as cash management and clearing activities), securities financing activities and cash placed with banks. A portion of the loans originated or acquired by the Firm’s wholesale businesses is generally retained on the balanc

judge: supported

verdict: [ ]

## claim-085  (baseline text-158)

**Claim:** Product and Brand-Related Issues: Litigation, product defects or impurities, product misuse, changing consumer perceptions of ingredients, negative perceptions of packaging (such as plastics or petroleum-based materials), lack of recyclability, concerns regarding labor, equality, inclusion, or social practices, allegations of product tampering, and the sale of counterfeit products

> [P1] litigation, defects or impurities in our products, product misuse, changing consumer perceptions of certain ingredients, negative perceptions of packaging (such as plastics and other petroleum-based materials), lack of recyclability or other environmental attributes, concerns about actual or alleged labor, equality and inclusion or social practices, cyber incidents, privacy failures or data losses, implementation or deployment of a controversial technology, negative views of ongoing operations in certain countries, allegations of product tampering, negative perceptions of or controversies related to employees or the distribution and sale of counterfeit products. Additionally, negative or ina

> [P2] The Procter & Gamble Company 5 liquidity and capital resources or significantly increase our cost of capital. In addition, we rely on top-tier banking partners in key markets around the world, who themselves face economic, societal, reputational, political and other risks, for access to credit and to facilitate collection, payment and supply chain finance programs. A disruption to one or more of these top-tier partners could impact our ability to draw on existing credit facilities or otherwise adversely affect our cash flows or the cash flows of our customers and vendors. BUSINESS OPERATIONS RISKS Our business results depend on our ability to manage disruptions in our global supply chain. Ou

> [P3] 4 The Procter & Gamble Company Uncertain economic or social conditions may adversely impact demand for our products or cause our customers and other business partners to suffer financial hardship, which could adversely impact our business. Our business could be negatively impacted by reduced demand for our products related to one or more significant local, regional or global economic or social disruptions. These disruptions have included and may include: a slow-down, recession or inflationary pressures in the general economy; reduced market growth rates; tighter credit markets for our suppliers, vendors or customers; a significant shift in government policies; significant social unrest; the

> [P4] As a company that manages a portfolio of consumer brands, our ongoing business model includes a certain level of acquisition, joint venture and divestiture activities. We must be able to successfully manage the impacts of these activities, while at the same time delivering against our business objectives. Specifically, our financial results have been and could be adversely impacted by the dilutive impacts from the loss of earnings associated with divested brands or dissolution of joint ventures. Our results of operations and cash flows have been and could be impacted by acquisitions or joint venture activities, if: 1) changes in the cash flows or other market-based assumptions cause the valu

> [P5] We discuss our expectations regarding future performance, events and outcomes, such as our business outlook and objectives in this Form 10-K, as well as in our quarterly and annual reports, current reports on Form 8-K, press releases and other written and oral communications. All statements, except for historical and present factual information, are “forward-looking statements” and are based on financial data and business plans available only as of the time the statements are made, which may become outdated or incomplete. We assume no obligation to update any forward-looking statements as a result of new information, future events or other factors, except to the extent required by law. Forwa

judge: supported

verdict: [ ]

## claim-086  (agent cross-182)

**Claim:** These increases were partially offset by a reduction in charges related to office space optimization efforts of $640 million.

> [P1] Research and Development The following table presents R&D expenses (in millions, except percentages): 38. Table of Contents Alphabet Inc. Year Ended December 31, 2023 2024 Research and development expenses $ 45,427 $ 49,326 Research and development expenses as a percentage of revenues 15 % 14 % R&D expenses increased $3.9 billion from 2023 to 2024, primarily driven by increases in employee compensation expenses of $1.5 billion, depreciation expense of $1.4 billion, and third-party services fees of $698 million, partially offset by a reduction in charges related to our office space optimization efforts of $640 million. The increase in employee compensation expenses was primarily driven by a $

> [P2] Research and Development The following table presents research and development expenses (in millions, except percentages): Year Ended December 31, 2024 2025 Research and development expenses $ 49,326 $ 61,087 Research and development expenses as a percentage of revenues 14 % 15 % Research and development expenses increased $11.8 billion from 2024 to 2025, primarily driven by increases in employee compensation expenses of $6.9 billion and depreciation expense of $2.4 billion. The increase in employee compensation expenses was primarily driven by an increase in SBC expenses of $4.2 billion, which included an increase in a valuation-based compensation charge related to Waymo. Sales and Marketin

> [P3] During the years ended December 31, 2023 and 2024, we spent $32.3 billion and $52.5 billion on capital expenditures, respectively. We expect to increase, relative to 2024, our investment in our technical infrastructure, including servers, network equipment, and data centers, to support the growth of our business and our long-term initiatives, in particular in support of AI products and services. Depreciation of our property and equipment commences when the deployment of such assets are completed and are ready for our intended use. For the years ended December 31, 2023 and 2024, our depreciation on property and equipment was $11.9 billion and $15.3 billion, respectively. Leases For the years

> [P4] Sales and marketing expenses $ 27,917 $ 27,808 Sales and marketing expenses as a percentage of revenues 9 % 8 % Sales and marketing expenses decreased $109 million from 2023 to 2024, due to a combination of factors, none of which were individually significant. General and Administrative The following table presents general and administrative expenses (in millions, except percentages): Year Ended December 31, 2023 2024 General and administrative expenses $ 16,425 $ 14,188 General and administrative expenses as a percentage of revenues 5 % 4 % General and administrative expenses decreased $2.2 billion from 2023 to 2024, primarily driven by a reduction in charges related to legal and other matt

> [P5] Other Information: •Dividend payments to stockholders of Class A, Class B, and Class C shares, which were first paid in June 2024, were $3.5 billion, $519 million, and $3.3 billion, respectively, totaling $7.4 billion for the year ended December 31, 2024. For additional information, see Note 11 of the Notes to Consolidated Financial Statements included in Item 8 of this Annual Report on Form 10-K. •Repurchases of Class A and Class C shares were $11.9 billion and $50.2 billion, respectively, totaling $62.0 billion for the year ended December 31, 2024. For additional information, see Note 11 of the Notes to Consolidated Financial Statements included in Item 8 of this Annual Report on Form 10-K

> [P6] 40. Table of Contents Alphabet Inc. expenses. Additionally, a decrease in the 2024 U.S. federal Foreign Derived Intangible Income tax deduction contributed to an increase in the effective tax rate. These factors were partially offset by an increase in stock-based compensation-related tax benefits in 2024. The OECD is coordinating negotiations among more than 140 countries with the goal of achieving consensus around substantial changes to international tax policies, including the implementation of a minimum global effective tax rate of 15%. Some countries have already implemented the legislation effective January 1, 2024, and we expect others to follow, however this did not have a material ef

> [F1] ticker = GOOGL, fiscal_year = 2024, metric = research_and_development, value = 49326000000.0

judge: supported

verdict: [ ]

## claim-087  (baseline text-142)

**Claim:** Chevron highlights estimates for decommissioning obligations, including for previously divested assets, as requiring significant estimates and assumptions

> [P1] Changes in management’s estimates and assumptions may have a material impact on the company’s consolidated financial statements and financial or operational performance in any given period In preparing the company’s periodic reports under the Securities Exchange Act of 1934, including its financial statements, Chevron’s management is required under applicable rules and regulations to make estimates and assumptions as of a specified date. These estimates and assumptions are based on management’s best estimates and experience as of that date and are subject to substantial risk and uncertainty. Materially different results may occur as circumstances change and additional information becomes kno

> [P2] perceived failure to pursue or fulfill such ambitions within the timelines we announce, or at all, or to satisfy various reporting standards and regulations could have a negative impact on the company’s reputation, investor sentiment, ratings outcomes for evaluating the company’s approach to ESG matters, stock price, and cost of capital and expose us to government enforcement actions and private litigation, among other material adverse impacts. GENERAL RISK FACTORS Changes in management’s estimates and assumptions may have a material impact on the company’s consolidated financial statements and financial or operational performance in any given period In preparing the company’s periodic repor

> [P3] For 2026, total worldwide environmental capital expenditures are estimated at $0.7 billion. These capital costs are in addition to the ongoing costs of complying with environmental regulations and the costs to remediate previously contaminated sites. Critical Accounting Estimates and Assumptions Management makes many estimates and assumptions in the application of accounting principles generally accepted in the United States of America (GAAP) that may have a material impact on the company’s consolidated financial statements and related disclosures and on the comparability of such information over different reporting periods. Such estimates and assumptions affect reported amounts of assets, l

> [P4] with the prevention, control, abatement or elimination of hazardous substances and pollutants from operating, closed or divested sites, and the decommissioning and restoration of sites. For 2025, total worldwide environmental capital expenditures are estimated at $0.6 billion. These capital costs are in addition to the ongoing costs of complying with environmental regulations and the costs to remediate previously contaminated sites. Critical Accounting Estimates and Assumptions Management makes many estimates and assumptions in the application of accounting principles generally accepted in the United States of America (GAAP) that may have a material impact on the company’s consolidated finan

> [P5] We will continue to invest in sales, marketing, product support infrastructure, and existing and advanced areas of technology, as well as acquisitions that align with our business strategy. Additions to property and equipment will continue, including new facilities, datacenters, and computer systems for research and development, sales and marketing, support, and administrative staff. We will continue to invest in capital expenditures to support growth in our cloud offerings and our investments in AI infrastructure and training. We have operating and finance leases for datacenters, corporate offices, research and development facilities, Microsoft Experience Centers, and certain equipment. We

judge: supported

verdict: [ ]

## claim-088  (agent text-157)

**Claim:** The company is subject to ongoing enforcement actions from supervisory authorities regarding cross-border data transfers.

> [P1] Further, we are subject to evolving laws and regulations that dictate whether, how, and under what circumstances we can transfer, process, or receive personal data, as well as ongoing enforcement actions from supervisory authorities related to cross-border transfers of personal data. The validity of various data transfer mechanisms we currently rely upon remains subject to legal, regulatory, and political developments globally, which may require us to adapt our existing arrangements. We face, and may continue to face, intellectual property infringement or misappropriation, violation of rights of publicity, and other claims that could be costly to defend, result in significant damage awards o

> [P2] 21. Table of Contents Alphabet Inc. Further, we are subject to evolving laws and regulations that dictate whether, how, and under what circumstances we can transfer, process and/or receive personal data, as well as ongoing enforcement actions from supervisory authorities related to cross-border transfers of personal data. The validity of various data transfer mechanisms we currently rely upon remains subject to legal, regulatory, and political developments globally, which may require us to adapt our existing arrangements. We face, and may continue to face, intellectual property infringement or misappropriation, violation of rights of publicity, and other claims that could be costly to defend

> [P3] Our international operations expose us to additional risks that could harm our business, reputation, financial condition, and operating results. 14. Table of Contents Alphabet Inc. Our international operations are significant to our revenues and net income, and we plan to continue to grow internationally. International revenues accounted for approximately 51% of our consolidated revenues in 2024. In addition to risks described elsewhere in this section, our international operations expose us to other risks, including the following: •restrictions on foreign ownership and investments, and stringent foreign exchange controls that might prevent us from repatriating cash earned in countries outsi

> [P4] of data protection laws, imposing specific obligations with respect to the processing of personal data, including required notices, consents, and opt-outs. Further, the increased risk of inadvertent disclosure of confidential information or personal data in connection with the utilization of AI technologies may result in stronger regulatory scrutiny, leading to legal and regulatory investigations and enforcement actions that could harm our business, even if unfounded. Adverse legal rulings, legislation, or regulation have resulted in, and may continue to result in, fines and orders requiring that we change our practices, which have had and could continue to have an adverse effect on how we p

> [P5] Our operations and financial results are subject to various risks and uncertainties, including but not limited to those described below, which could harm our business, reputation, financial condition, and operating results, and affect the trading price of our Class A and Class C stock. Risks Specific to our Company We generate a significant portion of our revenues from advertising. Reduced spending by advertisers, a loss of partners, or new and existing technologies that block ads online and/or affect our ability to personalize ads could harm our business. We generated more than 75% of total revenues from online advertising in 2024. Many of our advertisers, companies that distribute our prod

> [P6] Authorities around the world have adopted and are considering a number of legislative and regulatory proposals concerning data protection, data usage and portability, and encryption of user data. Additionally, the increasing adoption of AI technologies, which rely on the collection of large amounts of data and use of such data for training purposes, has led data protection authorities around the world to consider and adopt new and evolving interpretations of data protection laws, imposing specific obligations with respect to the processing of personal data, including required notices, consents, and opt-outs. Further, the increased risk of inadvertent disclosure of confidential information or

judge: supported

verdict: [ ]

## claim-089  (baseline text-092)

**Claim:** When assessing insurance coverage to diminish exposure, Eli Lilly considers policy coverage limits and exclusions, the potential for denial of coverage by the insurance company, the financial condition of the insurers, and the possibility of and length of time for collection.

> [P1] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P2] Litigation Liabilities and Other Contingencies Background and Uncertainties Litigation liabilities and other contingencies are, by their nature, uncertain and based upon complex judgments and probabilities. The factors we consider in developing our litigation liability reserves and other contingent liability amounts include the merits and jurisdiction of the litigation, the nature and the number of other similar current and past matters, the nature of the product and the current assessment of the science subject to the litigation, as applicable, and the likelihood of settlement and current state of settlement discussions, if any. In addition, we accrue for certain product liability claims in

> [P3] We are subject to a substantial number of claims, litigation, and investigations involving various current and historical products and practices. These claims relate to how we commercialize and/or how we price our products, product safety, our operations as well as contractual matters and other disputes. We have also filed lawsuits and taken other legal actions to protect our intellectual property and address unlawful practices. See Item 8, "Financial Statements and Supplementary Data—Note 16: Contingencies," for more information on certain matters. Like many companies in our industry, from time to time investigations into aspects of our business include inquiries, subpoenas, and other types

> [P4] initiated enforcement or other actions across industries to seek alignment with policy initiatives. Because of the nature of pharmaceutical products and our evolving business, we are, and could increasingly become, subject to large numbers of product liability claims for our previous, current, or future products, or to further litigation or investigations, including related to product safety, marketing, pricing, or other commercial practices. Some of these matters involve or may involve numerous plaintiffs and parties seeking large or indeterminate financial claims and may remain unresolved for several years. Such matters could negatively impact our reputation, affect our results of operatio

> [P5] We derive a significant percentage of our total revenue from relatively few products and sell our products through consolidated supply chain entities, which subjects us to various risks. We derived direct product and/or collaboration and other revenues of more than $3 billion for each of Mounjaro, Zepbound, Verzenio, Trulicity, Taltz, and Jardiance (including Glyxambi, Synjardy, and Trijardy XR) that collectively accounted for 82 percent of our total revenues in 2025. In particular, Mounjaro and Zepbound accounted for 56 percent of our total revenues in 2025, and we expect cardiometabolic health products will continue to represent a significant and growing portion of our business, revenues,

judge: supported

verdict: [ ]

## claim-090  (baseline cross-198)

**Claim:** Changes in operational working capital, excluding cash and debt, decreased cash in 2025 by $7.7 billion

> [P1] 2025 Cash provided by operating activities totaled $52.0 billion in 2025, $3.1 billion lower than 2024. The major source of funds was net income including noncontrolling interests of $29.8 billion, a decrease of $5.3 billion. The noncash provision for depreciation and depletion was $26.0 billion, up $2.6 billion from the prior year. The adjustment for the net gain on asset sales was $1.1 billion, a decrease of $0.1 billion. The adjustment for dividends received less than equity in current earnings of equity companies was an increase of $3.0 billion, compared to an increase of $0.2 billion in 2024. Changes in operational working capital, excluding cash and debt, decreased cash in 2025 by $7.7

> [P2] Our cost of products sold and SG&A are variable in nature to some extent. Accordingly, our discussion of these operating costs focuses primarily on relative margins rather than the absolute year-over-year changes in total costs. The primary drivers of changes in gross margin are input costs (energy and other commodities), pricing impacts, geographic mix (for example, gross margins in North America are generally higher than the Company average for similar products), product mix (for example, the Beauty segment has higher gross margins than the Company average), foreign exchange rate fluctuations (in situations where certain input costs may be tied to a different functional currency than the u

> [P3] Table of Contents Financial Table of Contents MANAGEMENT’S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS LIQUIDITY AND CAPITAL RESOURCES Sources and Uses of Cash (millions of dollars) 2025 2024 2023 Net cash provided by/(used in) Operating activities 51,970 55,022 55,369 Investing activities (25,927) (19,938) (19,274) Financing activities (39,081) (42,789) (34,297) Effect of exchange rate changes 532 (676) 105 Increase/(decrease) in cash and cash equivalents (12,506) (8,381) 1,903 Total cash and cash equivalents (December 31) 10,681 23,187 31,568 Total cash and cash equivalents were $10.7 billion at the end of 2025, down $12.5 billion from the prior year. The major

> [P4] Total cash and cash equivalents were $23.2 billion at the end of 2024, down $8.4 billion from the prior year. The major sources of funds in 2024 were net income including noncontrolling interests of $35.1 billion, the adjustment for the noncash provision of $23.4 billion for depreciation and depletion, proceeds from asset sales of $5.0 billion, and other investing activities of $1.9 billion, and cash acquired from mergers and acquisitions of $0.8 billion. The major uses of funds included spending for additions to property, plant, and equipment of $24.3 billion; dividends to shareholders of $16.7 billion; the purchase of ExxonMobil stock of $19.6 billion; debt repayment of $5.9 billion; addit

> [P5] We define free cash flow as net cash provided by operating activities in a period minus payments for property and equipment made in that period. We had net cash provided by operating activities of $36.4 billion, $35.7 billion and $28.8 billion for fiscal 2025, 2024 and 2023, respectively. We generated free cash flow of $12.7 billion, $15.1 billion and $12.0 billion for fiscal 2025, 2024 and 2023, respectively. The increase in net cash provided by operating activities in fiscal 2025 is primarily due to an increase in cash provided by operating income and lapping the payment of accrued opioid legal charges in the prior year, partially offset by increased inventory purchases. Free cash flow for

judge: supported

verdict: [ ]

## claim-091  (agent sql-037)

**Claim:** Bank of America’s long‑term debt for fiscal 2024 was $283.279 billion

> [F1] ticker = BAC, fiscal_year = 2024, metric = long_term_debt, value = 283279000000.0

judge: supported

verdict: [ ]

## claim-092  (baseline text-086)

**Claim:** Litigation exposure and legal liability or regulatory fines

> [P1] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P2] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P3] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions, fires, product spills, severe weather, geological events, global health crises, such as epidemics and pandemics, labor disputes, geopolitical tensions, armed hostilities, terrorist or piracy attacks, sabotage, civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater technological challen

> [P4] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions; fires; product spills; severe weather; geological events; global health crises, such as epidemics and pandemics; labor disputes; geopolitical tensions and escalations; armed hostilities; terrorist or piracy attacks; sabotage; civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater techn

> [P5] We are subject to income taxation in numerous jurisdictions worldwide. We record deferred tax assets and liabilities to account for the expected future tax consequences of events that have been recognized in our financial statements and our tax returns. We routinely assess our deferred tax assets and reduce such assets by a valuation allowance if we deem it is more likely than not that some portion, or all, of the deferred tax assets will not be realized. In assessing the need for adjustments to existing valuation allowances, we consider all available positive and negative evidence. Positive evidence includes reversals of temporary differences, forecasts of future taxable income, assessment

judge: supported

verdict: [ ]

## claim-093  (agent text-142)

**Claim:** Accruals for estimated liabilities, including litigation reserves require significant estimates and assumptions that could materially affect Chevron's consolidated financial statements

> [P1] Changes in management’s estimates and assumptions may have a material impact on the company’s consolidated financial statements and financial or operational performance in any given period In preparing the company’s periodic reports under the Securities Exchange Act of 1934, including its financial statements, Chevron’s management is required under applicable rules and regulations to make estimates and assumptions as of a specified date. These estimates and assumptions are based on management’s best estimates and experience as of that date and are subject to substantial risk and uncertainty. Materially different results may occur as circumstances change and additional information becomes kno

> [P2] perceived failure to pursue or fulfill such ambitions within the timelines we announce, or at all, or to satisfy various reporting standards and regulations could have a negative impact on the company’s reputation, investor sentiment, ratings outcomes for evaluating the company’s approach to ESG matters, stock price, and cost of capital and expose us to government enforcement actions and private litigation, among other material adverse impacts. GENERAL RISK FACTORS Changes in management’s estimates and assumptions may have a material impact on the company’s consolidated financial statements and financial or operational performance in any given period In preparing the company’s periodic repor

> [P3] For 2026, total worldwide environmental capital expenditures are estimated at $0.7 billion. These capital costs are in addition to the ongoing costs of complying with environmental regulations and the costs to remediate previously contaminated sites. Critical Accounting Estimates and Assumptions Management makes many estimates and assumptions in the application of accounting principles generally accepted in the United States of America (GAAP) that may have a material impact on the company’s consolidated financial statements and related disclosures and on the comparability of such information over different reporting periods. Such estimates and assumptions affect reported amounts of assets, l

> [P4] with the prevention, control, abatement or elimination of hazardous substances and pollutants from operating, closed or divested sites, and the decommissioning and restoration of sites. For 2025, total worldwide environmental capital expenditures are estimated at $0.6 billion. These capital costs are in addition to the ongoing costs of complying with environmental regulations and the costs to remediate previously contaminated sites. Critical Accounting Estimates and Assumptions Management makes many estimates and assumptions in the application of accounting principles generally accepted in the United States of America (GAAP) that may have a material impact on the company’s consolidated finan

> [P5] We will continue to invest in sales, marketing, product support infrastructure, and existing and advanced areas of technology, as well as acquisitions that align with our business strategy. Additions to property and equipment will continue, including new facilities, datacenters, and computer systems for research and development, sales and marketing, support, and administrative staff. We will continue to invest in capital expenditures to support growth in our cloud offerings and our investments in AI infrastructure and training. We have operating and finance leases for datacenters, corporate offices, research and development facilities, Microsoft Experience Centers, and certain equipment. We

> [P6] We will continue to invest in sales, marketing, product support infrastructure, and existing and advanced areas of technology, as well as acquisitions that align with our business strategy. Additions to property and equipment will continue, including new facilities, datacenters, and computer systems for research and development, sales and marketing, support, and administrative staff. We will continue to invest in capital expenditures to support growth in our cloud offerings and our investments in AI training and other infrastructure. We have operating and finance leases for datacenters and related infrastructure, servers and network equipment, corporate offices, and research and development

judge: supported

verdict: [ ]

## claim-094  (baseline cross-178)

**Claim:** Management stated that the increase in net income in 2025 was primarily due to a higher gross margin, which was partially offset by increased marketing, selling, and administrative expenses and research and development expenses.

> [P1] (Tables present dollars in millions, except per-share data, and numbers may not add due to rounding) General Management's discussion and analysis of results of operations and financial condition is intended to assist the reader in understanding and assessing significant changes and trends related to our results of operations and financial position. This discussion and analysis should be read in conjunction with Item 8, "Financial Statements and Supplementary Data." Certain statements in this Item 7 constitute forward-looking statements. Various risks and uncertainties, including those discussed in "Forward-Looking Statements" and Item 1A, "Risk Factors," may cause our actual results, financi

> [P2] 2,910 3,280 (11) Income taxes 5,091 2,090 144 Effective tax rate 19.8 % 16.5 % Gross margin as a percent of revenue in 2025 increased 1.7 percentage points compared with 2024, primarily driven by favorable product mix and improved cost of production, partially offset by lower realized prices. Research and development expenses increased 21 percent in 2025, primarily driven by continued investments in our early and late-stage portfolio. Marketing, selling, and administrative expenses increased 29 percent in 2025, primarily driven by promotional efforts supporting ongoing and planned launches.

> [P3] Percent change 43 % 48 % 45 % In the U.S., the volume increase and the lower realized prices in 2025 were primarily driven by Mounjaro and Zepbound. Outside the U.S., the volume increase in 2025 was primarily driven by Mounjaro. The following table summarizes our revenue, including net product revenue and collaboration and other revenue, by product in 2025 compared with 2024:

> [P4] In addition to our cash and cash equivalents, we held total investments of $2.9 billion and $3.4 billion as of December 31, 2025 and 2024, respectively. As of December 31, 2025, we had approximately $902 million of unfunded commitments to invest in venture capital funds, which we anticipate will be paid over a period of up to 10 years. See Note 7 to the consolidated financial statements for additional information. We paid $3.0 billion in 2025 for acquired IPR&D primarily related to the acquisitions of Scorpion's PI3Kα inhibitor program STX-478 and of SiteOne. We paid $3.3 billion in 2024 for acquired IPR&D primarily related to the acquisition of Morphic. See Note 4 to the consolidated financ

> [P5] As of December 31, 2025, a 5 percent change in the amount of uncertain tax positions and the valuation allowance would result in a change in net income of $160 million and $61 million, respectively. LEGAL AND REGULATORY MATTERS Information relating to certain legal proceedings can be found in Note 16 to the consolidated financial statements and is incorporated here by reference.

judge: supported

verdict: [ ]

## claim-095  (baseline text-132)

**Claim:** Apple identifies relative price and performance as a principal competitive factor important to its success

> [P1] The markets for the Company’s products and services are highly competitive and are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. The markets in which the Company competes are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements by competitors. Many of the Company’s competitors seek to compete primarily through aggressive pricing and very low cost structures, and by imitating the Company’s products and infringing on its intellec

> [P2] The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs and develops nearly the entire solution for its products, including the hardware, operating system, numerous software applications and related services. Principal competitive factors important to the Company include price, product and service features (including security features), relative price and performance, product and service quality and reliability, design innovation, a strong third-party software and accessories ecosystem, marketing and distribution capability, service and suppor

> [P3] The Company’s products and services are offered in highly competitive global markets. These markets are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. These markets are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements. The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs an

> [P4] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number of factors, including timely and successful development, market accepta

> [P5] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, navigate global regulatory requirements and barriers to market access, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number

judge: supported

verdict: [ ]

## claim-096  (baseline text-086)

**Claim:** Negative impacts on public health, safety, the environment, economic security, or national security

> [P1] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P2] If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environm

> [P3] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions, fires, product spills, severe weather, geological events, global health crises, such as epidemics and pandemics, labor disputes, geopolitical tensions, armed hostilities, terrorist or piracy attacks, sabotage, civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater technological challen

> [P4] Our operations are subject to a variety of hazards and risks that require significant and continuous oversight, such as the monitoring, prevention or mitigation of or protection from explosions; fires; product spills; severe weather; geological events; global health crises, such as epidemics and pandemics; labor disputes; geopolitical tensions and escalations; armed hostilities; terrorist or piracy attacks; sabotage; civil unrest or cyberattacks. Our operations are subject to additional hazards concerning exposure to and potential release of pollutants and toxic substances, as well as other environmental hazards and risks. For example, offshore activities may pose incrementally greater techn

> [P5] We are subject to income taxation in numerous jurisdictions worldwide. We record deferred tax assets and liabilities to account for the expected future tax consequences of events that have been recognized in our financial statements and our tax returns. We routinely assess our deferred tax assets and reduce such assets by a valuation allowance if we deem it is more likely than not that some portion, or all, of the deferred tax assets will not be realized. In assessing the need for adjustments to existing valuation allowances, we consider all available positive and negative evidence. Positive evidence includes reversals of temporary differences, forecasts of future taxable income, assessment

judge: supported

verdict: [ ]

## claim-097  (baseline text-132)

**Claim:** Apple identifies corporate reputation as a principal competitive factor important to its success

> [P1] The markets for the Company’s products and services are highly competitive and are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. The markets in which the Company competes are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements by competitors. Many of the Company’s competitors seek to compete primarily through aggressive pricing and very low cost structures, and by imitating the Company’s products and infringing on its intellec

> [P2] The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs and develops nearly the entire solution for its products, including the hardware, operating system, numerous software applications and related services. Principal competitive factors important to the Company include price, product and service features (including security features), relative price and performance, product and service quality and reliability, design innovation, a strong third-party software and accessories ecosystem, marketing and distribution capability, service and suppor

> [P3] The Company’s products and services are offered in highly competitive global markets. These markets are characterized by aggressive price competition, downward pressure on gross margins, continual improvement in product performance, and price sensitivity on the part of consumers and businesses. These markets are further defined by frequent introduction of new products and services, short product life cycles, evolving industry standards, and rapid adoption of technological advancements. The Company’s ability to compete successfully depends heavily on ensuring the continuing and timely introduction of innovative new products, services and technologies to the marketplace. The Company designs an

> [P4] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number of factors, including timely and successful development, market accepta

> [P5] To remain competitive and stimulate customer demand, the Company must successfully manage frequent introductions and transitions of products and services. Due to the highly volatile and competitive nature of the markets and industries in which the Company competes, the Company must continually introduce new products, services and technologies, enhance existing products and services, effectively stimulate customer demand for new and upgraded products and services, navigate global regulatory requirements and barriers to market access, and successfully manage the transition to these new and upgraded products and services. The success of new product and service introductions depends on a number

judge: supported

verdict: [ ]

## claim-098  (baseline text-136)

**Claim:** Target identifies its revenue streams as the sale of merchandise to customers, as well as other sources including Roundel, credit card profit sharing related to the Target Circle Card program, the third‑party digital marketplace Target Plus, and membership fees.

> [P1] We generate revenue through a variety of other sources, including Roundel, which provides advertising services to vendors and other third parties, including marketplace sellers; credit card profit sharing related to our Target Circle Card program; our third-party digital marketplace, Target Plus; membership fees; and others. Customer Loyalty Program We seek to drive customer loyalty and trip frequency through our Target Circle™ program, which provides benefits to guests that vary depending on their engagement with the program through one or more of the following offerings: •a free membership providing deals and bonuses including instant discounts and Target Circle Rewards offerings redeemabl

> [P2] (53 weeks) 2024 (52 weeks) 2025 (52 weeks) $107.4 $106.6 $104.8 (a) 2023 consisted of 53 weeks. The extra week in 2023 contributed $1.7 billion of Net Sales. TARGET CORPORATION 2025 Form 10-K 3 BUSINESS Table of Contents Index to Financial Statements Merchandise Sales by Fulfillment Channel Financial Highlights For information on key financial highlights, see Part II, Item 7, Management's Discussion and Analysis of Financial Condition and Results of Operations (MD&A).

> [P3] Strategy Target’s strategy is grounded in our purpose to help all families discover the joy of everyday life and our ambition to be the most delightful experience in retail. We differentiate through design, style, and value, and a curated multi-category assortment delivered across stores and digital channels. Our strategy is centered on four priorities. Lead with Merchandising Authority. Curating design-led, trend-right assortments that combine quality, newness, and value. We focus on categories and brands where we can offer a distinctive and relevant experience for our guests. Elevate the Guest Experience. Elevating the guest experience by making shopping easy, inspiring, and friendly. Our

> [P4] Our year-end cash and cash equivalents balance increased to $5.5 billion from $4.8 billion in 2024. Our cash and cash equivalents balance includes short-term investments of $4.6 billion and $3.9 billion as of January 31, 2026, and February 1, 2025, respectively. Our investment policy is designed to preserve principal and liquidity of our short-term investments. This policy allows investments in large money market funds or in highly rated direct short-term instruments that mature in 60 days or less. We also place dollar limits on our investments in individual funds or instruments. Operating Cash Flows Cash flows provided by operating activities were $6.6 billion in 2025 compared with $7.4 bil

> [P5] Distribution Most merchandise is distributed to our stores through our network of distribution centers. Common carriers ship merchandise to and from our distribution centers. Vendors or third-party distributors ship certain food and beverage items and other merchandise directly to our stores. Merchandise sold through our digital channels is distributed to our guests through guest pick-up at our stores, via common carriers (from stores, supply chain facilities, vendors, and third-party distributors), and same-day delivery. Our stores fulfill the majority of digitally originated sales, which allows improved product availability, faster fulfillment times, reduced shipping costs, and allows us t

judge: supported

verdict: [ ]

## claim-099  (baseline text-098)

**Claim:** Visa’s U.S. retrospective responsibility plan addresses monetary liabilities from settlements of, or final judgments in, U.S. covered litigation.

> [P1] We have entered into loss sharing agreements that reduce our potential liability in connection with certain litigation. However, our U.S. retrospective responsibility plan only addresses monetary liabilities from settlements of, or final judgments in, the U.S. covered litigation. The plan’s mechanisms include the use of the U.S. litigation escrow account. The accrual related to the U.S. covered litigation could be either higher or lower than the U.S. litigation escrow account balance. Our Europe retrospective responsibility plan only covers Visa Europe territory covered litigation (and resultant liabilities and losses) relating to the covered period, subject to certain limitations, and does

> [P2] Assumptions and judgment. We evaluate the likelihood of a potential loss from legal or regulatory proceedings to which we are a party. We record a liability for such claims when a loss is deemed probable and the amount can be reasonably estimated. Significant judgment may be required in the determination of both probability and whether a loss is reasonably estimable. Our judgments are inherently subjective and based on a number of factors, including management’s understanding of the legal or regulatory profile and the specifics of each proceeding, our history with similar matters, advice of internal and external legal counsel and management’s best estimate of incurred loss. As additional inf

> [P3] Under the U.S. retrospective responsibility plan, we recover the monetary liabilities related to the U.S. covered litigation through a downward adjustment to the rate at which shares of our class B-1 and class B-2 common stock ultimately convert into shares of class A common stock. During fiscal 2025, basic and diluted earnings per class A common stock increased $0.01 and was unchanged, respectively, as a result of the downward adjustments of the class B-1 and B-2 common stock conversion rates during the period. During fiscal 2024 and 2023, basic and diluted earnings per class A common stock were unchanged in both fiscal years, as a result of the downward adjustments of the class B-1 and B-2

> [P4] U.S. Litigation escrow account. Pursuant to the terms of the U.S. retrospective responsibility plan, which was created to insulate Visa and our class A common stockholders from financial liability for certain litigation cases, we maintain a U.S. litigation escrow account from which monetary liabilities from settlements of, or judgments in, the U.S. covered litigation will be payable. As these funds are restricted for the sole purpose of making payments related to the U.S. covered litigation matters, we do not rely on them for other operational needs. See Note 5—U.S. and Europe Retrospective Responsibility Plans and Note 20—Legal Matters to our consolidated financial statements included in It

> [P5] Credit facility. We have an unsecured revolving credit facility, which is maintained to ensure the integrity of the payment card settlement process and for general corporate purposes. As of September 30, 2025, there were no amounts outstanding under the credit facility. See Note 10—Debt to our consolidated financial statements included in Item 8 of this report. Senior notes. In May 2025, we issued Euro-denominated fixed-rate senior notes in a public offering in an aggregate principal amount of €3.5 billion ($3.9 billion), with maturities ranging between 3 and 19 years. See Note 10—Debt to our consolidated financial statements included in Item 8 of this report. U.S. Litigation escrow account.

judge: supported

verdict: [ ]
