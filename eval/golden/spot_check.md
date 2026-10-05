# Golden-set spot check

For each case: is the question clear and standalone, and does the evidence fully
support the reference answer? Mark `verdict: [x]` to keep, or `verdict: [bad] reason`.

## text-112  (text)

**Q:** What therapeutic indications are associated with TREMFYA (guselkumab) as disclosed in J&J's 2024 10-K?

**Reference answer:** Treatment of Ulcerative Colitis (QUASAR), Subcutaneous Induction for treatment of patients with Ulcerative Colitis (ASTRO), Subcutaneous Induction for treatment of patients with Crohn's Disease (GRAVITI), Treatment of Patients with Crohn's Disease (GALAXI), Treatment of Patients with Pediatric Psoriasis


> RYBREVANT Treatment for Non-Small Cell Lung Cancer 2L (MARIPOSA-2) • • SIMPONI (golimumab) Treatment of Patients with Pediatric Ulcerative Colitis • • SPRAVATO (esketamine) monotherapy Treatment of Patients with Treatment Resistant Depression (TRD4005) • STELARA (ustekinumab) Treatment of Patients with Pediatric Crohn's Disease • TREMFYA (guselkumab) Treatment of Patients with Ulcerative Colitis (QUASAR) • • TREMFYA (guselkumab) Subcutaneous Induction for treatment of patients with Ulcerative Colitis (ASTRO) • TREMFYA (guselkumab) Subcutaneous Induction for treatment of patients with Crohn's Disease (GRAVITI) • • TREMFYA (guselkumab) Treatment of Patients with Crohn's Disease (GALAXI) • • TREMFYA (guselkumab) Treatment of Patients with Pediatric Psoriasis • UPTRAVI (selexipag) Treatment of Patients with Pediatric Pulmonary Arterial Hypertension (SALTO) •

LLM judge: The question is clear, specific to J&J's 2024 10-K, and not answerable from general knowledge. The reference answer lists the therapeutic indications for TREMFYA that are directly supported by the provided evidence.

verdict: [ ]

## sql-068  (sql)

**Q:** What was Microsoft's operating income for fiscal year 2023?

**Reference answer:** Microsoft's operating income in fiscal 2023 was $88.52 billion.

- fact: MSFT operating_income FY2023 = 88,523,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-131  (text)

**Q:** What effect does a strong U.S. dollar have on Eli Lilly's operations, given its net foreign currency exposure?

**Reference answer:** We are a net receiver of foreign currencies, and our results of operations are adversely impacted when the U.S. dollar is strong compared to foreign currencies.


> These and similar events have adversely affected, and may continue to adversely affect, us, our business partners, and our customers. For more details, see Item 1, "Business—Regulations and Private Payer Actions Affecting Pharmaceutical Pricing, Reimbursement, and Access." In addition to developments related to our business or financial results, or those of our competitors, uneven economic growth, downturns, or other negative global developments, could also undermine our growth or result in significant and sudden declines in the trading price of our common stock and market capitalization. •Changes in foreign currency rates, interest rate risks, and inflation or deflation affect our results of operations. As a global company, we face foreign currency risk exposure from fluctuating currency exchange rates, interest rate risk from our exposure to floating and variable interest rates, and existing and expected rates of inflation or deflation in the U.S. and other jurisdictions, each of which impacts our results of operations. In recent periods, significant fluctuations in currency rates and inflation have impacted our results of operations. We are a net receiver of foreign currencies,

LLM judge: The question is standalone, specific to Eli Lilly's net foreign currency exposure, and the reference answer directly reflects the evidence stating that Eli Lilly is a net receiver of foreign currencies and its results are adversely impacted when the U.S. dollar is strong.

verdict: [ ]

## cross-196  (cross)

**Q:** For Eli Lilly's fiscal year 2024, what specific factors drove the 102% increase in net income to $10.59 billion, and which product lines were the primary contributors to the revenue growth that supported this result?

**Reference answer:** The increase in net income was primarily driven by higher gross margin, partially offset by increased R&D, marketing, selling, and administrative expenses, as well as asset impairment and restructuring charges. The underlying revenue growth was primarily driven by Mounjaro, Zepbound, and Verzenio, partially offset by Trulicity.

- fact: LLY net_income FY2024 = 10,590,000,000.00 USD

> (Tables present dollars in millions, except per-share data) General Management's discussion and analysis of results of operations and financial condition is intended to assist the reader in understanding and assessing significant changes and trends related to our results of operations and financial position. This discussion and analysis should be read in conjunction with Item 8, "Financial Statements and Supplementary Data." Certain statements in this Item 7 constitute forward-looking statements. Various risks and uncertainties, including those discussed in "Forward-Looking Statements" and Item 1A, "Risk Factors," may cause our actual results, financial position, and cash generated from operations to differ from these forward-looking statements. EXECUTIVE OVERVIEW This section provides an overview of our financial results, our clinical development pipeline, and other matters affecting our company and industry. Financial Results The following table summarizes certain financial information: Year Ended December 31, Percent Change 2024 2023 Revenue $ 45,042.7 $ 34,124.1 32 Net income 10,590.0 5,240.4 102 Earnings per share - diluted 11.71 5.80 102 Revenue increased in 2024 driven by in

LLM judge: The question is self‑contained, specific to Eli Lilly’s FY2024 results, and not answerable from general knowledge. The reference answer restates evidence that net income rise was due to higher gross margin (partially offset by higher R&D, marketing, selling & administrative expenses, and asset impai

verdict: [ ]

## sql-042  (sql)

**Q:** What was Caterpillar's revenue for fiscal 2023?

**Reference answer:** Caterpillar's revenue in fiscal 2023 was $67.06 billion.

- fact: CAT revenue FY2023 = 67,060,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## sql-048  (sql)

**Q:** What was UPS's revenue for fiscal year 2025?

**Reference answer:** UPS's revenue in fiscal 2025 was $88.66 billion.

- fact: UPS revenue FY2025 = 88,661,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## cross-167  (cross)

**Q:** For Amazon's fiscal year 2024, what was the total revenue, and according to the MD&A, what were the primary drivers behind the 19% growth in AWS sales?

**Reference answer:** Amazon's total revenue for fiscal year 2024 was $637.96 billion. The 19% growth in AWS sales was primarily driven by increased customer usage, partially offset by pricing changes resulting from long-term customer contracts.

- fact: AMZN revenue FY2024 = 637,959,000,000.00 USD

> Table of Contents AWS sales increased 19% in 2024, compared to the prior year. The sales growth primarily reflects increased customer usage, partially offset by pricing changes primarily driven by long-term customer contracts. Operating Expenses Information about operating expenses is as follows (in millions): Year Ended December 31, 2023 2024 Operating Expenses: Cost of sales $ 304,739 $ 326,288 Fulfillment 90,619 98,505 Technology and infrastructure 85,622 88,544 Sales and marketing 44,370 43,907 General and administrative 11,816 11,359 Other operating expense (income), net 767 763 Total operating expenses $ 537,933 $ 569,366 Year-over-year Percentage Growth (Decline): Cost of sales 6 % 7 % Fulfillment 7 9 Technology and infrastructure 17 3 Sales and marketing 5 (1) General and administrative (1) (4) Other operating expense (income), net (39) (1) Percent of Net Sales: Cost of sales 53.0 % 51.1 % Fulfillment 15.8 15.4 Technology and infrastructure 14.9 13.9 Sales and marketing 7.7 6.9 General and administrative 2.1 1.8 Other operating expense (income), net 0.1 0.1 Cost of Sales Cost of sales primarily consists of the purchase price of consumer products, inbound and outbound shippi

LLM judge: The question is standalone, specific to Amazon FY2024 revenue and AWS growth drivers, and the reference answer is fully supported by the provided evidence.

verdict: [ ]

## sql-054  (sql)

**Q:** What were Home Depot's total assets for fiscal year 2023?

**Reference answer:** Home Depot's total assets in fiscal 2023 was $76.53 billion.

- fact: HD total_assets FY2023 = 76,530,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-123  (text)

**Q:** What new reportable segments will PepsiCo use for its international food businesses beginning in the first quarter of 2025?

**Reference answer:** Latin America Foods, Europe, Middle East and Africa (EMEA), and Other International Foods (which includes the foods businesses in APAC and India).


> In North America, the food businesses, FLNA and QFNA, will be reported together as PepsiCo Foods North America. These changes do not impact our PBNA segment. Internationally, the foods businesses in LatAm, Europe, AMESA and APAC will be reorganized into three reportable segments: Latin America Foods, Europe, Middle East and Africa (EMEA), and Other International Foods. Other International Foods will include the foods businesses in APAC and India, currently part of AMESA. Our international franchise beverage businesses that were part of our LatAm, Europe, AMESA and APAC segments will be reported as International Beverages Franchise. The company-owned bottling businesses operating internationally are all located within EMEA and will be reported in the newly created EMEA segment. Our historical segment reporting will be recast beginning first quarter 2025 to reflect the new organizational structure.

LLM judge: The question is clear, specific to PepsiCo’s segment reporting change, and answer is fully supported by the provided evidence.

verdict: [ ]

## cross-179  (cross)

**Q:** How did foreign currency exchange rate fluctuations, including hedging activities, impact Coca‑Cola’s 2025 net income of $13.11 billion?

**Reference answer:** Foreign currency exchange rate fluctuations, including hedging activities, caused a 12% decline in operating income in 2025, which contributed to the net income of $13.11 billion.

- fact: KO net_income FY2025 = 13,107,000,000.00 USD

> In 2024 and 2023, our operating income was impacted by the weighted-average fluctuations in exchange rates for foreign currencies in which the Company conducted operations (all operating currencies) and for certain individual currencies. These currencies strengthened (weakened) against the U.S. dollar as follows: Year Ended December 31, 2024 2023 All operating currencies (5) % (2) % Australian dollar (1) (5) Brazilian real (7) 3 British pound 3 2 Chinese yuan (2) (7) Euro — 3 Indian rupee (1) (6) Japanese yen (7) (7) Mexican peso (3) 14 Philippine peso (3) (3) South African rand 1 (11) The percentages in the table above do not include the effects of our hedging activities and, therefore, do not reflect the actual impact of fluctuations in foreign currency exchange rates on our operating results. Our hedging activities are designed to mitigate, over time, a portion of the potentially unfavorable impact of exchange rate fluctuations on our net income. The total impact of foreign currency exchange rate fluctuations on net operating revenues, including the effect of our hedging activities, was a decrease of 5% and 4% in 2024 and 2023, respectively. The total impact of foreign currency

LLM judge: The question is specific, understandable without additional context, and asks about a detail that is answered by the evidence. The reference answer is fully supported by the provided filing excerpts, which describe a 12% decrease in operating income due to foreign currency fluctuations (including he

verdict: [ ]

## sql-044  (sql)

**Q:** What were Costco's capital expenditures for fiscal year 2022?

**Reference answer:** Costco's capital expenditures in fiscal 2022 was $3.89 billion.

- fact: COST capital_expenditures FY2022 = 3,891,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-159  (text)

**Q:** Which commercial jet models are currently in production under Boeing's Commercial Airplanes segment, and which derivatives are under development?

**Reference answer:** The 737 narrow‑body, 767, 777 and 787 are in production; development continues on the 777X program and the 737‑7 and 737‑10 derivatives.


> The Boeing Company, together with its subsidiaries (herein referred to as “Boeing,” the “Company,” “we,” “us,” “our”), is one of the world’s major aerospace firms. We are organized based on the products and services we offer. We operate in three reportable segments: •Commercial Airplanes (BCA); •Defense, Space & Security (BDS); •Global Services (BGS). Commercial Airplanes Segment This segment develops, produces and markets commercial jet aircraft principally to the commercial airline industry worldwide. We are a leading producer of commercial aircraft and offer a family of commercial jetliners designed to meet a broad spectrum of global passenger and cargo requirements of airlines. This family of commercial jet aircraft in production includes the 737 narrow-body model and the 767, 777 and 787 wide-body models. Development continues on the 777X program and the 737-7 and 737-10 derivatives. Defense, Space & Security Segment This segment engages in the research, development, production and modification of manned and unmanned military aircraft and weapons systems for strike, surveillance and mobility, including fighter and trainer aircraft; vertical lift, including rotorcraft and tilt-

LLM judge: The question is standalone, specific to Boeing's Commercial Airplanes segment, and not answerable from general knowledge. The reference answer is fully supported by the provided evidence, which lists the 737 narrow‑body, 767, 777, and 787 as in production and mentions development of the 777X and 737

verdict: [ ]

## text-084  (text)

**Q:** What was the total amount of Class A and Class C share repurchases by Alphabet in fiscal 2025?

**Reference answer:** $45.4 billion


> Other Information: 32. Table of Contents Alphabet Inc. •In 2025, we entered into definitive agreements to acquire Wiz, a leading cloud security platform, for $32.0 billion, and Intersect, a provider of data center and energy infrastructure solutions, for $4.8 billion in cash plus the assumption of debt. Both acquisitions are expected to close in 2026, subject to customary closing conditions, including the receipt of regulatory approvals. •In 2025, we issued senior unsecured notes for net proceeds of $37.3 billion, to be used for general corporate purposes. •OI&E of $29.8 billion for the year ended December 31, 2025 included net gains on equity securities of $24.1 billion, primarily related to unrealized gains on our non-marketable equity securities. •Other Bets operating loss of $7.5 billion for the year ended December 31, 2025 included a $2.1 billion employee compensation charge recognized in the fourth quarter for Waymo, primarily reflected in research and development expenses, based on estimated stock valuation. In February 2026, Waymo announced an investment round of $16.0 billion, the significant majority of which was funded by Alphabet. •Changes to U.S. tax law enacted on Jul

LLM judge: The question is clear, specific to Alphabet’s 2025 share repurchases, and not answerable from general knowledge. It is phrased in original wording. The reference answer of $45.4 billion is directly supported by the evidence stating the total repurchases of Class A and Class C shares were $45.4 billi

verdict: [ ]

## sql-039  (sql)

**Q:** What is Meta's long-term debt balance for fiscal 2024?

**Reference answer:** Meta's long-term debt in fiscal 2024 was $28.83 billion.

- fact: META long_term_debt FY2024 = 28,826,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## sql-052  (sql)

**Q:** What was Costco's operating income for fiscal year 2025?

**Reference answer:** Costco's operating income in fiscal 2025 was $10.38 billion.

- fact: COST operating_income FY2025 = 10,383,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-141  (text)

**Q:** What was Eli Lilly's effective tax rate in fiscal 2025 and what were the primary factors that drove the increase from fiscal 2024?

**Reference answer:** Eli Lilly’s effective tax rate was 19.8 % in fiscal 2025 versus 16.5 % in fiscal 2024. The increase was driven by an unfavorable jurisdictional mix of earnings and U.S. tax law changes in 2025, as well as the impact of non‑deductible acquired IPR&D charges, which had a larger effect in 2024.


> Acquired in-process research and development (IPR&D) charges recognized in 2025 were primarily related to the acquisitions of Scorpion Therapeutics, Inc.'s (Scorpion) PI3Kα inhibitor program STX-478 and of SiteOne Therapeutics, Inc. (SiteOne). Acquired IPR&D charges recognized in 2024 were primarily related to the acquisition of Morphic Holding, Inc. (Morphic). See Note 4 to the consolidated financial statements for additional information. Our effective tax rate was 19.8 percent in 2025 compared with an effective tax rate of 16.5 percent in 2024, primarily driven by unfavorable impacts related to the jurisdictional mix of earnings and U.S. tax law changes in 2025 relative to 2024. The effective tax rates for both periods were unfavorably impacted by non-deductible acquired IPR&D charges, with a larger impact occurring in 2024. See Note 14 to the consolidated financial statements for additional information. Operating Results—2024 For a discussion of our results of operations pertaining to 2024 and 2023 see Item 7, "Management's Discussion and Analysis of Results of Operations and Financial Condition" in our Annual Report on Form 10-K for the year ended December 31, 2024. FINANCIAL C

LLM judge: The question is standalone, specific to Eli Lilly's effective tax rate and drivers of change, and the reference answer is fully supported by the provided evidence.

verdict: [ ]

## text-137  (text)

**Q:** What actuarial assumptions does UPS use to calculate the costs of its defined benefit pension and postretirement medical plans?

**Reference answer:** UPS calculates the costs of its company-sponsored defined benefit pension and postretirement medical plans using discount rates, expected returns on plan assets, healthcare cost trend rates, inflation, compensation increase rates, mortality rates, and coordination of benefits with plans not sponsored by UPS.


> MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS Reversal of Income Tax Valuation Allowance We previously recorded non-GAAP adjustments for transactions that resulted in capital loss deferred tax assets not expected to be realized. As a result of property sales during 2025, we now expect all of these capital losses to be realized. We supplement our presentation with non-GAAP adjusted financial measures that exclude the impact of the reversals of the valuation allowances against these deferred tax assets as we believe such treatment is consistent with how the valuation allowance was initially established. One-Time Payment for International Regulatory Matter We have excluded the impact in 2024 of a payment to settle a previously-disclosed international tax regulatory matter. We do not believe this payment was a component of our ongoing operations and we do not expect this or similar payments to recur. Expense for Regulatory Matter We have excluded the impact in 2024 of an expense to settle a previously disclosed regulatory matter. We do not believe this was a component of our ongoing operations and we do not expect this or similar expenses to recu

LLM judge: The question is specific to UPS and asks about actuarial assumptions for its defined benefit pension and postretirement medical plans. The reference answer lists the assumptions exactly as stated in the provided evidence, fully supported by the filing. It meets all criteria for a valid evaluation qu

verdict: [ ]

## sql-047  (sql)

**Q:** What was Chevron's research and development expense for fiscal year 2025?

**Reference answer:** Chevron's research and development expense in fiscal 2025 was $427.0 million.

- fact: CVX research_and_development FY2025 = 427,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-091  (text)

**Q:** Which product lines are included in Procter & Gamble's Grooming segment?

**Reference answer:** Appliances, Female Blades & Razors, Male Blades & Razors, Pre- and Post-Shave Products, Other Grooming


> Skin Care (2) (Facial Moisturizers, Cleaners and Treatments) Olay, SK-II Grooming 8% 10% Grooming (Appliances, Female Blades & Razors, Male Blades & Razors, Pre- and Post-Shave Products, Other Grooming) Braun, Gillette, Venus Health Care 14% 15% Oral Care (Toothbrushes, Toothpastes, Other Oral Care) Crest, Oral-B Personal Health Care (Gastrointestinal, Pain Relief, Rapid Diagnostics, Respiratory, Vitamins/Minerals/Supplements, Other Personal Health Care) Metamucil, Neurobion, Pepto-Bismol, Vicks Fabric & Home Care 36% 35% Fabric Care (Fabric Enhancers, Laundry Additives, Laundry Detergents) Ariel, Downy, Gain, Tide

LLM judge: The question is self‑contained, specific to P&G’s filing, and not answerable from general knowledge. The reference answer directly lists the product lines (Appliances, Female Blades & Razors, Male Blades & Razors, Pre‑ and Post‑Shave Products, Other Grooming) that are explicitly provided in the evid

verdict: [ ]

## sql-053  (sql)

**Q:** What were Nike's cash and cash equivalents as of fiscal year 2025?

**Reference answer:** Nike's cash and cash equivalents in fiscal 2025 was $7.46 billion.

- fact: NKE cash_and_equivalents FY2025 = 7,464,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## cross-171  (cross)

**Q:** For Walmart's fiscal 2026, what was the total revenue, and according to the MD&A, what specific factors drove the increase in net sales while noting the impact of currency exchange rates?

**Reference answer:** Total revenue was $713.16 billion. The increase in net sales was primarily driven by strong positive comparable sales across U.S. segments and international markets, specifically due to increases in average ticket and transactions, growth in unit volumes, strength in eCommerce, and strong sales in grocery, health and wellness, and general merchandise. Net sales were negatively impacted by $2.8 billion due to fluctuations in currency exchange rates.

- fact: WMT revenue FY2026 = 713,163,000,000.00 USD

> Unit counts at period end 10,771 10,616 10,623 Retail square feet at period end 1,053 1,053 1,056 (1) Membership and other income includes membership fees and other items such as rental and tenant income, recycling income, gift card breakage income, as well as other income from corporate campus facilities. (2) Gross profit is defined as net sales less cost of sales. Operating expenses refers to operating, selling, general and administrative expenses. Our total revenues increased $32.9 billion or 5.1% and $36.8 billion or 6.0% for fiscal 2025 and 2024, respectively, when compared to the previous fiscal year. These increases in revenues were primarily due to increases in net sales, which increased $31.9 billion or 5.0% and $36.8 billion or 6.1% for fiscal 2025 and 2024, respectively, when compared to the previous fiscal year. The increases were primarily due to strong positive comparable sales across our U.S. segments and international markets, driven primarily by growth in transactions and unit volumes, which included strength in eCommerce as well as strong sales in grocery, and health and wellness. Net sales were negatively impacted by $3.2 billion and positively impacted by $3.0 b

LLM judge: The question is standalone, specific to Walmart's fiscal 2026 revenue and drivers of net sales increase, and not answerable from general knowledge. The reference answer is fully supported by the provided evidence, accurately restating the revenue figure, the factors driving net sales growth, and the

verdict: [ ]

## text-138  (text)

**Q:** What drove the increase in RWA under the Standardized approach for Bank of America at December 31, 2024?

**Reference answer:** client activity in Global Markets and lending activity in GWIM, Global Banking and Consumer Banking


> At December 31, 2024, CET1 capital was $201.1 billion, an increase of $6.2 billion from December 31, 2023, primarily due to earnings, partially offset by capital distributions. Tier 1 capital increased $135 million primarily driven by the increase in CET1 capital, partially offset by preferred stock redemptions. Total capital under the Standardized approach increased $4.0 billion primarily due to an increase in subordinated debt, adjusted allowance for credit losses included in Tier 2 capital, and the increase in Tier 1 capital. RWA under the Standardized approach, which yielded the lower CET1 capital ratio at December 31, 2024, increased $44.5 billion during 2024 to $1,696 billion primarily driven by client activity in Global Markets and lending activity in GWIM, Global Banking and Consumer Banking. Supplementary leverage exposure at December 31, 2024 increased $142.0 billion primarily driven by increased activity in Global Markets and ALM activities in All Other. Bank of America 50

LLM judge: The question is specific, standalone, and not answerable from general knowledge. The reference answer directly matches the evidence stating that the RWA increase was primarily driven by client activity in Global Markets and lending activity in GWIM, Global Banking and Consumer Banking, thus it is fu

verdict: [ ]

## sql-045  (sql)

**Q:** Could you share Boeing's cash provided by operating activities for fiscal 2022?

**Reference answer:** Boeing's cash provided by operating activities in fiscal 2022 was $3.51 billion.

- fact: BA operating_cash_flow FY2022 = 3,512,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## cross-174  (cross)

**Q:** Visa reported total revenue of $40.00 billion for fiscal 2025. According to the MD&A, what were the primary drivers behind the increase in Service revenue and Data processing revenue during this period?

**Reference answer:** Service revenue increased primarily due to 7% growth in nominal payments volume, select pricing modifications, and card benefits. Data processing revenue increased primarily due to 10% growth in processed transactions and select pricing modifications.

- fact: V revenue FY2025 = 40,000,000,000.00 USD

> For the Years Ended September 30, % Change(1) 2024 2023 2022 2024 vs. 2023 2023 vs. 2022 (in millions, except percentages) Service revenue $ 16,114 $ 14,826 $ 13,361 9 % 11 % Data processing revenue 17,714 16,007 14,438 11 % 11 % International transaction revenue 12,665 11,638 9,815 9 % 19 % Other revenue 3,197 2,479 1,991 29 % 24 % Client incentives (13,764) (12,297) (10,295) 12 % 19 % Net revenue $ 35,926 $ 32,653 $ 29,310 10 % 11 % (1)Figures in the table may not recalculate exactly due to rounding. Percentage changes are calculated based on unrounded numbers. •Service revenue increased in fiscal 2024 over the prior year primarily due to 7% growth in nominal payments volume. •Data processing revenue increased in fiscal 2024 over the prior year primarily due to 10% growth in processed transactions. •International transaction revenue increased in fiscal 2024 over the prior year primarily due to growth in nominal cross-border volume of 14%, excluding transactions within Europe, partially offset by lower volatility of a broad range of currencies. •Other revenue increased in fiscal 2024 over the prior year primarily due to growth in marketing and consulting services and select pricin

LLM judge: The question is standalone, specific to Visa's FY2025 MD&A, and not answerable from general knowledge. The reference answer directly restates the evidence about the drivers of Service and Data processing revenue, fully supported by the provided filing excerpts.

verdict: [ ]

## sql-061  (sql)

**Q:** What was ConocoPhillips's operating cash flow for fiscal year 2025?

**Reference answer:** ConocoPhillips's cash provided by operating activities in fiscal 2025 was $19.80 billion.

- fact: COP operating_cash_flow FY2025 = 19,796,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-087  (text)

**Q:** Which specific technologies and projects is ExxonMobil's Low Carbon Solutions (LCS) business unit focused on developing and deploying?

**Reference answer:** Carbon capture and storage (CCS), hydrogen, lower-emission fuels, lithium, breakthrough energy efficiency processes, and advanced energy-saving materials.


> Technology and lower-emission solutions. Achieving societal ambitions to reduce greenhouse gas emissions and ultimately achieve net zero will require new technologies and added infrastructure to reduce the cost and increase the scalability of alternative energy sources, as well as technologies such as carbon capture and storage (CCS). CCS technologies, focused initially on capturing and sequestering CO2 emissions from high-carbon intensity industrial activities, can assist in meeting society’s objective to mitigate atmospheric greenhouse gas levels while also helping ensure the availability of the reliable and affordable energy the world requires. ExxonMobil has established a Low Carbon Solutions (LCS) business unit and is continuing efforts in our existing businesses to advance the development and deployment of these technologies and projects, including CCS, hydrogen, lower-emission fuels, and lithium, breakthrough energy efficiency processes, advanced energy-saving materials, and other technologies. The Company’s efforts include both in-house research and development as well as collaborative efforts with leading universities and with commercial partners involved in new energy tec

LLM judge: The question is standalone, specific, and phrased in the analyst's own words. The reference answer lists the exact technologies mentioned in the evidence, fully supported by the filing, making it a valid, grounded response.

verdict: [ ]

## cross-177  (cross)

**Q:** What factors contributed to Alphabet's $350.02B revenue in fiscal 2024, including the impact of mobile advertising, newer formats, and device mix changes?

**Reference answer:** Advertising revenues from mobile and newer formats, with lower margins, and changes in device mix, geographic mix, partner mix, TAC rate, and product mix.

- fact: GOOGL revenue FY2024 = 350,018,000,000.00 USD

> Our users are accessing our products and services via diverse devices and modalities beyond traditional desktop, such as smartphones, wearables, connected TVs, and smart home devices, and want to be able to be connected no matter where they are or what they are doing. We are focused on expanding our products and services to stay in front of these trends in order to maintain and grow our business. We benefit from advertising revenues generated from different channels, including mobile, and newer advertising formats. The margins from these channels and newer products have generally been lower than those from traditional desktop search. Additionally, as the market for a particular device type or modality matures, our advertising revenues may be affected. For example, changing dynamics within the global smartphone market, such as increased market saturation in developed countries, can affect our mobile advertising revenues. We expect TAC paid to our distribution partners and Google Network partners to increase as our revenues grow and TAC as a percentage of our advertising revenues ("TAC rate") to be affected by changes in device mix; geographic mix; partner agreement terms; partner mi

LLM judge: The question is clear, specific to Alphabet's fiscal 2024 revenue and asks for contributing factors, which are answered using evidence about mobile advertising, newer formats, and changes in device, geographic, partner, and product mix. The reference answer is fully supported by the provided filing

verdict: [ ]

## cross-197  (cross)

**Q:** For ExxonMobil's fiscal year 2024, what were the primary drivers behind the $55.02 billion in cash provided by operating activities, specifically regarding the impact of net income, depreciation and depletion, and changes in operational working capital?

**Reference answer:** The $55.02 billion in cash provided by operating activities was primarily driven by net income including noncontrolling interests of $35.1 billion (a decrease of $2.3 billion from the prior year) and a noncash provision for depreciation and depletion of $23.4 billion (an increase of $2.8 billion). These were partially offset by a $1.8 billion decrease in cash due to changes in operational working capital, excluding cash and debt.

- fact: XOM operating_cash_flow FY2024 = 55,022,000,000.00 USD

> 2024 Cash provided by operating activities totaled $55.0 billion in 2024, $0.3 billion lower than 2023. The major source of funds was net income including noncontrolling interests of $35.1 billion, a decrease of $2.3 billion. The noncash provision for depreciation and depletion was $23.4 billion, up $2.8 billion from the prior year. The adjustment for the net gain on asset sales was $1.2 billion, an increase of $0.7 billion. The adjustment for dividends received less than equity in current earnings of equity companies was an increase of $0.2 billion, compared to an increase of $0.5 billion in 2023. Changes in operational working capital, excluding cash and debt, decreased cash in 2024 by $1.8 billion. 2023 Cash provided by operating activities totaled $55.4 billion in 2023, $21.4 billion lower than 2022. The major source of funds was net income including noncontrolling interests of $37.4 billion, a decrease of $20.2 billion. The noncash provision for depreciation and depletion was $20.6 billion, down $3.4 billion from the prior year. The adjustment for the net gain on asset sales was $0.5 billion, a decrease of $0.5 billion. The adjustment for dividends received less than equity in

LLM judge: The question is specific to ExxonMobil's FY2024 cash flow and is understandable on its own. The reference answer accurately restates the evidence about net income, depreciation and depletion, and working capital changes, fully supported by the provided filing excerpt.

verdict: [ ]

## cross-195  (cross)

**Q:** For Boeing's fiscal year 2025, what was the reported gross profit, and which specific fixed-price development programs were cited as the primary drivers for the $1,377 million decrease in earnings from operations due to cumulative catch-up adjustments?

**Reference answer:** Boeing's fiscal 2025 gross profit was $4.29 billion. The primary drivers for the $1,377 million decrease in earnings from operations were losses recognized on the KC-46A Tanker, VC-25B, T-7A Red Hawk, MQ-25, and Commercial Crew programs.

- fact: BA gross_profit FY2025 = 4,289,000,000.00 USD

> Revenue and cost estimates for all significant long-term contract performance obligations are reviewed and reassessed quarterly. Changes in these estimates could result in recognition of cumulative catch-up adjustments to the contract’s inception to date revenues, cost of sales and profit in the period in which such changes are made. Changes in revenue and cost estimates could also result in a reach-forward loss or an adjustment to a reach-forward loss which would be recorded immediately in earnings. Net cumulative catch-up adjustments for changes in estimated revenues and costs at completion across all long-term contracts, including the impact of estimated losses on unexercised options, increased Loss from operations by $6,562 million, $2,943 million and $5,253 million in 2024, 2023 and 2022, respectively, and were primarily due to losses recognized on the KC-46A Tanker, T-7A Red Hawk, Commercial Crew, VC-25B, and MQ-25 programs. These are all fixed-price development programs, and there is ongoing risk that similar losses may have to be recognized in future periods on these and/or other programs. Due to the significance of judgment in the estimation process described above, it is

LLM judge: The question is standalone, specific to Boeing's FY2025 gross profit and the fixed‑price development programs driving the $1,377 million earnings decrease. The reference answer directly states the gross profit ($4.29 billion) and lists the programs (KC‑46A Tanker, VC‑25B, T‑7A Red Hawk, MQ‑25, Comme

verdict: [ ]

## text-086  (text)

**Q:** What potential negative consequences does ConocoPhillips identify if its IT, OT, or SCADA systems are breached?

**Reference answer:** If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environment, economic security, or national security; financial impacts; business interruption; reputational damage; loss of employee, supplier, contractor, partner and/or public trust; reimbursement or other costs; increased compliance costs; regulatory investigations; litigation exposure and legal liability or regulatory fines; penalties or other external intervention.


> If our data, IT, operational technology (OT), including industrial control and supervisory control and data acquisition (SCADA) systems were to be breached, damaged or disrupted due to a cybersecurity incident or cyber-attack (directly, indirectly through third parties or through the IT networks, servers, software, or infrastructure on which they rely), we could be subject to serious negative consequences. These consequences could include physical damage to production, distribution or storage assets; delay or prevention of delivery to markets; disruption or prevention of accurate accounting for production and settlement of transactions; negative impacts on public health, safety, the environment, economic security, or national security; financial impacts; business interruption; reputational damage; loss of employee, supplier, contractor, partner and/or public trust; reimbursement or other costs; increased compliance costs; regulatory investigations; litigation exposure and legal liability or regulatory fines; penalties or other external intervention. Although we have business continuity plans in place, our operations may be adversely affected by significant and widespread disruption

LLM judge: The question is clear, self‑contained, and asks for specific details that are only found in the filing. The reference answer accurately restates the list of negative consequences provided in the evidence, fully supported by the source text.

verdict: [ ]

## sql-041  (sql)

**Q:** What was Target's net income for fiscal year 2023?

**Reference answer:** Target's net income in fiscal 2023 was $4.14 billion.

- fact: TGT net_income FY2023 = 4,138,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## sql-064  (sql)

**Q:** What was JPMorgan Chase's net cash provided by operating activities for fiscal year 2023?

**Reference answer:** JPMorgan Chase's cash provided by operating activities in fiscal 2023 was $12.97 billion.

- fact: JPM operating_cash_flow FY2023 = 12,974,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-104  (text)

**Q:** What potential financial and operational costs does Eli Lilly anticipate if its IT systems or third‑party service providers fail to protect confidential information?

**Reference answer:** Significant costs, including fines, penalties, litigation, compliance obligations, lost productivity, manufacturing disruption, and remediation and recovery costs.


> Important confidential information owned by us, our business partners, or other third parties is stored in our information systems, networks, and facilities or those of third parties. This includes valuable trade secrets and intellectual property, clinical trial information, corporate strategic plans, marketing plans, customer information, and personal information, such as employee and patient information (collectively, confidential information). We also rely, to a large extent, on the efficient and uninterrupted operation of complex information technology systems, infrastructure, cloud technologies, and hardware (together, IT systems), some of which are within our control and some of which are within the control of third parties, to accumulate, process, store, and transmit large amounts of confidential information and other data. We are subject to a variety of evolving and developing laws and regulations around the world related to privacy, data protection, and data security. Maintaining the security, confidentiality, integrity, and availability of our IT systems and confidential information is vital to our business. Our failure, or the failure of our third-party service providers

LLM judge: The question is specific to Eli Lilly and asks about anticipated financial and operational costs of IT or third‑party failures, which is clearly answered by the reference answer that lists fines, penalties, litigation, compliance obligations, lost productivity, manufacturing disruption, and remediat

verdict: [ ]

## cross-183  (cross)

**Q:** For UPS in fiscal 2025, what specific operational and financial factors drove the decrease in cash provided by operating activities to $8.45 billion?

**Reference answer:** The decrease was driven by unfavorable working capital changes (lower U.S. Domestic Package volume reducing payables, higher incentive compensation, and higher income tax payments due to a 2024 deferred payment for Hurricane Helene relief) and a reduction in net income, partially offset by $730 million in cash proceeds from the new factored accounts receivable program.

- fact: UPS operating_cash_flow FY2025 = 8,450,000,000.00 USD

> 2024 2023 Net income $ 5,782 $ 6,708 Non-cash operating activities(1) 5,622 5,437 Pension and postretirement medical benefit plan contributions (Company-sponsored plans) (1,524) (1,393) Hedge margin receivables and payables (90) (444) Income tax receivables and payables 313 (294) Changes in working capital and other non-current assets and liabilities 33 366 Other operating activities (14) (142) Net cash from operating activities $ 10,122 $ 10,238 (1) Represents depreciation and amortization, gains and losses on derivative transactions and foreign currency exchange, deferred income taxes, allowances for expected credit losses, pension and postretirement medical benefit plan (income) expense, stock compensation expense, changes in casualty self-insurance reserves, goodwill and other asset impairment charges and other non-cash items. Net cash from operating activities decreased $116 million in 2024, driven by the following: •The reduction in net income. •Increased 401(k) plan contributions. The decreases were partially offset by: •An increase in our U.S income tax position as a result of the tax deferral related to Hurricane Helene. •A payment in 2023 for deferred employer payroll tax

LLM judge: The question is specific to UPS fiscal 2025 cash flow and asks for the drivers of the decrease, which is answerable only from the filing. The reference answer lists the operational and financial factors (unfavorable working capital changes, lower domestic volume, higher incentive compensation, highe

verdict: [ ]

## sql-066  (sql)

**Q:** What was JPMorgan Chase's diluted EPS for fiscal year 2022?

**Reference answer:** JPMorgan Chase's diluted earnings per share in fiscal 2022 was $12.09 per share.

- fact: JPM eps_diluted FY2022 = 12.09 USD/shares

LLM judge: computed from financial_facts

verdict: [ ]

## sql-060  (sql)

**Q:** What were UnitedHealth's capital expenditures for fiscal year 2025?

**Reference answer:** UnitedHealth's capital expenditures in fiscal 2025 was $3.62 billion.

- fact: UNH capital_expenditures FY2025 = 3,622,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-108  (text)

**Q:** How does Pfizer expect generic competition to impact the pricing and volume of its branded small molecule products in China in 2025 and beyond?

**Reference answer:** Pfizer expects intensified competition from generic manufacturers in China due to the expansion of the QCE process and the continuation of the VBP program, which may result in price cuts and volume loss for some of its products.


> Generic Products. Generic pharmaceutical manufacturers pose one of the biggest competitive challenges to our branded small molecule products because they can market a competing version of our product after the expiration or loss of our patent protection and often charge much less. Several competitors regularly challenge our product patents before their expiration. Generic competitors often operate without large R&D expenses, as well as without costs of conveying medical information about products to the medical community. In addition, the approval process in the U.S. and in the EU exempts generics from costly and time-consuming clinical trials to demonstrate their safety and efficacy, allowing generic manufacturers to rely on the safety and efficacy data of the innovator product. In China, for example, given the expansion of the QCE process and continuation of the VBP program, we expect to continue to face intensified competition by certain generic manufacturers in 2025 and beyond, which has and may continue to result in price cuts and volume loss of some of our products. In addition, generic versions of competitors’ branded products have and may continue to compete with our produc

LLM judge: The question is specific to Pfizer's expectations about generic competition affecting pricing and volume of its branded small molecule products in China from 2025 onward, and the reference answer is directly supported by the provided evidence.

verdict: [ ]

## text-076  (text)

**Q:** What specific operational and financial consequences does Nike identify if its primary footwear contract manufacturers fail to meet quality standards or make timely shipments?

**Reference answer:** Nike states that if primary footwear contract manufacturers fail to make timely shipments, do not meet quality standards, or otherwise fail to deliver product in accordance with plans, it could have a material adverse effect on the company's results of operations.


> We rely on a concentrated source base of contract manufacturers to supply a significant portion of our footwear products. We rely upon a concentrated amount of contract manufacturers, which we do not own or operate, to manufacture all of the footwear products we sell, see "Manufacturing" for additional information. Our ability to meet our customers' needs depends on our ability to maintain a steady supply of products from our contract manufacturers. If one or more of our significant suppliers were to sever their relationship with us or significantly alter the terms of our relationship, including due to changes in applicable trade policies, or be unable to perform, we may not be able to obtain replacement products in a timely manner, which could have a material adverse effect on our business operations, sales, financial condition or results of operations. Additionally, if any of our primary footwear contract manufacturers fail to make timely shipments, do not meet our quality standards or otherwise fail to deliver us product in accordance with our plans, there could be a material adverse effect on our results of operations. Certain of our contract manufacturers are highly specialize

LLM judge: The answer is self‑contained, names Nike, is directly supported by the filing excerpt, provides a specific detail not inferable from general knowledge, is paraphrased rather than a verbatim copy, and addresses a relevant analyst question about operational and financial impact.

verdict: [ ]

## sql-056  (sql)

**Q:** What were Meta's total assets for fiscal year 2023?

**Reference answer:** Meta's total assets in fiscal 2023 was $229.62 billion.

- fact: META total_assets FY2023 = 229,623,000,000.00 USD

LLM judge: computed from financial_facts

verdict: [ ]

## text-078  (text)

**Q:** What was the percentage change in revenue for Microsoft in fiscal year 2026 compared to fiscal year 2025?

**Reference answer:** 18%


> 2026 2025 Percentage Change Revenue $ 331,839 $ 281,724 18% Gross margin 225,465 193,893 16% Operating income 155,237 128,528 21% Net income 133,749 101,832 31% Diluted earnings per share 17.95 13.64 32% Adjusted net income (non-GAAP) 128,786 105,452 22% Adjusted diluted earnings per share (non-GAAP) 17.28 14.13 22% Adjusted net income and adjusted diluted earnings per share (“EPS”) are non-GAAP financial measures. These non-GAAP financial measures exclude net gains and losses from investments in OpenAI. Refer to the Non-GAAP Financial Measures section below for a reconciliation of our financial results reported in accordance with GAAP to non-GAAP financial results. Fiscal Year 2026 Compared with Fiscal Year 2025 Revenue increased $50.1 billion or 18% driven by growth in Microsoft Cloud. Intelligent Cloud revenue increased driven by Azure. Productivity and Business Processes revenue increased driven by Microsoft 365 Commercial cloud. More Personal Computing revenue decreased driven by XBOX (formerly Gaming), offset in part by growth in Search advertising. Cost of revenue increased $18.5 billion or 21% driven by growth in Microsoft Cloud. Gross margin increased $31.6 billion or 16%

LLM judge: The answer directly addresses the specific analyst question about Microsoft’s FY2026 vs FY2025 revenue change, is fully supported by the evidence (table and narrative stating an 18% increase), is not a verbatim excerpt, and provides information not inferable from general knowledge.

verdict: [ ]
