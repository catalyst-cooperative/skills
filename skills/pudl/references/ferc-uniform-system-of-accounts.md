# FERC Uniform System of Accounts — Electric Utility Account Listing

**Authoritative source**: 18 C.F.R. Part 101 — *Uniform System of Accounts Prescribed
for Public Utilities and Licensees Subject to the Provisions of the Federal Power Act*
[18 C.F.R. Part 101 on eCFR](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-C/part-101)

> **Do not load the eCFR URL into context in its entirety — it is a very large page.**
> If you need the full regulatory text, download it and cache it locally, then search
> selectively. The account listing below (compiled from the NARUC summary publication)
> covers account numbers and short descriptions; consult the CFR for the full
> definitional text of any individual account.

Accounts marked **(Major only)** apply only to Major utilities; those marked
**(Nonmajor only)** apply only to non-Major utilities; unmarked accounts apply to both.

---

> **For agent use, query [`ferc_accounts.json`](../assets/ferc_accounts.json)**
> **with jq or DuckDB rather than reading this file into context.**
> The full account listing below is for human reference only.

---

## Querying the machine-readable index

Use [`ferc_accounts.json`](../assets/ferc_accounts.json) for all programmatic lookups.
Fields: `account`, `description`, `chart`, `section`, `group`, `operation_type`,
`major_only`, `nonmajor_only`, `reserved`.

### jq examples

```bash
# Look up a specific account
jq '.[] | select(.account == "182.3")' assets/ferc_accounts.json

# Find all accounts in a numeric range
jq '[.[] | select(.account | test("^18[0-9]"))] | .[] | {account, description}' \
  assets/ferc_accounts.json

# List all O&M transmission expense accounts
jq '[.[] | select(.chart == "om_expenses" and .section == "2. Transmission Expenses")] |
    .[] | {account, description, operation_type}' assets/ferc_accounts.json

# Find all Major-only accounts
jq '[.[] | select(.major_only)] | .[].account' assets/ferc_accounts.json
```

### DuckDB examples

```sql
-- Find accounts by keyword
SELECT account, description, chart, section
FROM read_json('assets/ferc_accounts.json')
WHERE description ILIKE '%depreciation%';

-- All transmission O&M expense accounts
SELECT account, description, operation_type
FROM read_json('assets/ferc_accounts.json')
WHERE chart = 'om_expenses' AND section = '2. Transmission Expenses'
ORDER BY account;

-- Which Form 1 schedules reference accounts in the 550-557 range
SELECT a.account, a.description AS account_desc, s.schedule, s.title
FROM read_json('assets/ferc_accounts.json') a
JOIN read_json('assets/ferc1_schedules.json') s
  ON list_contains(s.ferc_accounts, a.account)
WHERE a.account BETWEEN '550' AND '557'
ORDER BY a.account;
```

---

## Full account listing

> *Human reference — agents should use the JSON sidecar above.*

<!-- BEGIN GENERATED CONTENT -->

## Balance Sheet Chart of Accounts

### Assets and Other Debits

#### 1. Utility Plant

| Account | Description |
|---------|-------------|
| 101 | Electric plant in service *(Major only)* |
| 101.1 | Property under capital leases |
| 102 | Electric plant purchased or sold |
| 103 | Experimental electric plant unclassified *(Major only)* |
| 103.1 | Electric plant in process of reclassification *(Nonmajor only)* |
| 104 | Electric plant leased to others |
| 105 | Electric plant held for future use |
| 106 | Completed construction not classified — Electric *(Major only)* |
| 107 | Construction work in progress — Electric |
| 108 | Accumulated provision for depreciation of electric utility plant *(Major only)* |
| 109 | [Reserved] |
| 110 | Accumulated provision for depreciation and amortization of electric utility plant *(Nonmajor only)* |
| 111 | Accumulated provision for amortization of electric utility plant *(Major only)* |
| 112 | [Reserved] |
| 113 | [Reserved] |
| 114 | Electric plant acquisition adjustments |
| 115 | Accumulated provision for amortization of electric plant acquisition adjustments *(Major only)* |
| 116 | Other electric plant adjustments |
| 118 | Other utility plant |
| 119 | Accumulated provision for depreciation and amortization of other utility plant |
| 120.1 | Nuclear fuel in process of refinement, conversion, enrichment and fabrication *(Major only)* |
| 120.2 | Nuclear fuel materials and assemblies — Stock account *(Major only)* |
| 120.3 | Nuclear fuel assemblies in reactor *(Major only)* |
| 120.4 | Spent nuclear fuel *(Major only)* |
| 120.5 | Accumulated provision for amortization of nuclear fuel assemblies *(Major only)* |
| 120.6 | Nuclear fuel under capital leases *(Major only)* |

#### 2. Other Property and Investments

| Account | Description |
|---------|-------------|
| 121 | Nonutility property |
| 122 | Accumulated provision for depreciation and amortization of nonutility property |
| 123 | Investment in associated companies *(Major only)* |
| 123.1 | Investment in subsidiary companies *(Major only)* |
| 124 | Other investments |
| 125 | Sinking funds *(Major only)* |
| 126 | Depreciation fund *(Major only)* |
| 127 | Amortization fund — Federal *(Major only)* |
| 128 | Other special funds *(Major only)* |
| 129 | Special funds *(Nonmajor only)* |

#### 3. Current and Accrued Assets

| Account | Description |
|---------|-------------|
| 130 | Cash and working funds *(Nonmajor only)* |
| 131 | Cash *(Major only)* |
| 132 | Interest special deposits *(Major only)* |
| 133 | Dividend special deposits *(Major only)* |
| 134 | Other special deposits *(Major only)* |
| 135 | Working funds *(Major only)* |
| 136 | Temporary cash investments |
| 141 | Notes receivable |
| 142 | Customer accounts receivable |
| 143 | Other accounts receivable |
| 144 | Accumulated provision for uncollectible accounts — credit |
| 145 | Notes receivable from associated companies |
| 151 | Fuel stock *(Major only)* |
| 152 | Fuel stock expenses undistributed *(Major only)* |
| 153 | Residuals *(Major only)* |
| 154 | Plant materials and operating supplies |
| 155 | Merchandise *(Major only)* |
| 156 | Other materials and supplies *(Major only)* |
| 157 | Nuclear materials held for sale *(Major only)* |
| 158.1 | Allowance inventory |
| 158.2 | Allowances withheld |
| 163 | Stores expense undistributed *(Major only)* |
| 165 | Prepayments |
| 171 | Interest and dividends receivable *(Major only)* |
| 172 | Rents receivable *(Major only)* |
| 173 | Accrued utility revenues *(Major only)* |
| 174 | Miscellaneous current and accrued assets |
| 175 | Derivative instrument assets |
| 176 | Derivative instrument assets — Hedges |

#### 4. Deferred Debits

| Account | Description |
|---------|-------------|
| 181 | Unamortized debt expense |
| 182.1 | Extraordinary property losses |
| 182.2 | Unrecovered plant and regulatory study costs |
| 182.3 | Other regulatory assets |
| 183 | Preliminary survey and investigation charges *(Major only)* |
| 184 | Clearing accounts *(Major only)* |
| 185 | Temporary facilities *(Major only)* |
| 186 | Miscellaneous deferred debits |
| 187 | Deferred losses from disposition of utility plant |
| 188 | Research, development, and demonstration expenditures *(Major only)* |
| 189 | Unamortized loss on reacquired debt |
| 190 | Accumulated deferred income taxes |

### Liabilities and Other Credits

#### 5. Proprietary Capital

| Account | Description |
|---------|-------------|
| 201 | Common stock issued |
| 202 | Common stock subscribed *(Major only)* |
| 203 | Common stock liability for conversion *(Major only)* |
| 204 | Preferred stock issued |
| 205 | Preferred stock subscribed *(Major only)* |
| 206 | Preferred stock liability for conversion *(Major only)* |
| 207 | Premium on capital stock *(Major only)* |
| 208 | Donations received from stockholders *(Major only)* |
| 209 | Reduction in par or stated value of capital stock *(Major only)* |
| 210 | Gain on resale or cancellation of reacquired capital stock *(Major only)* |
| 211 | Miscellaneous paid-in capital |
| 212 | Installments received on capital stock |
| 213 | Discount on capital stock |
| 214 | Capital stock expense |
| 215 | Appropriated retained earnings |
| 215.1 | Appropriated retained earnings — Amortization reserve, Federal |
| 216 | Unappropriated retained earnings |
| 216.1 | Unappropriated undistributed subsidiary earnings *(Major only)* |
| 217 | Reacquired capital stock |
| 218 | Noncorporate proprietorship *(Nonmajor only)* |
| 219 | Accumulated other comprehensive income |

#### 6. Long-Term Debt

| Account | Description |
|---------|-------------|
| 221 | Bonds |
| 222 | Reacquired bonds *(Major only)* |
| 223 | Advances from associated companies |
| 224 | Other long-term debt |
| 225 | Unamortized premium on long-term debt |
| 226 | Unamortized discount on long-term debt — Debit |

#### 7. Other Noncurrent Liabilities

| Account | Description |
|---------|-------------|
| 227 | Obligations under capital lease — noncurrent |
| 228.1 | Accumulated provision for property insurance |
| 228.2 | Accumulated provision for injuries and damages |
| 228.3 | Accumulated provision for pensions and benefits |
| 228.4 | Accumulated miscellaneous operating provisions |
| 229 | Accumulated provision for rate refunds |
| 230 | Asset retirement obligations |

#### 8. Current and Accrued Liabilities

| Account | Description |
|---------|-------------|
| 231 | Notes payable |
| 233 | Notes payable to associated companies |
| 235 | Customer deposits |
| 236 | Taxes accrued |
| 237 | Interest accrued |
| 238 | Dividends declared *(Major only)* |
| 239 | Matured long-term debt *(Major only)* |
| 240 | Matured interest *(Major only)* |
| 241 | Tax collections payable *(Major only)* |
| 242 | Miscellaneous current and accrued liabilities |
| 243 | Obligations under capital leases — current |
| 244 | Derivative instrument liabilities |
| 245 | Derivative instrument liabilities — Hedges |

#### 9. Deferred Credits

| Account | Description |
|---------|-------------|
| 251 | [Reserved] |
| 252 | Customer advances for construction |
| 253 | Other deferred credits |
| 254 | Other regulatory liabilities |
| 255 | Accumulated deferred investment tax credits |
| 256 | Deferred gains from disposition of utility plant |
| 257 | Unamortized gain on reacquired debt |
| 281 | Accumulated deferred income taxes — Accelerated amortization property |
| 282 | Accumulated deferred income taxes — Other property |
| 283 | Accumulated deferred income taxes — Other |

## Electric Plant Chart of Accounts (Account 101)

### 1. Intangible Plant

| Account | Description |
|---------|-------------|
| 301 | Organization |
| 302 | Franchises and consents |
| 303 | Miscellaneous intangible plant |

### 2. Production Plant

#### A. Steam Production

| Account | Description |
|---------|-------------|
| 310 | Land and land rights |
| 311 | Structures and improvements |
| 312 | Boiler plant equipment |
| 313 | Engines and engine-driven generators |
| 314 | Turbogenerator units |
| 315 | Accessory electric equipment |
| 316 | Miscellaneous power plant equipment |
| 317 | Asset retirement costs for steam production plant |

#### B. Nuclear Production

| Account | Description |
|---------|-------------|
| 320 | Land and land rights *(Major only)* |
| 321 | Structures and improvements *(Major only)* |
| 322 | Reactor plant equipment *(Major only)* |
| 323 | Turbogenerator units *(Major only)* |
| 324 | Accessory electric equipment *(Major only)* |
| 325 | Miscellaneous power plant equipment *(Major only)* |
| 326 | Asset retirement costs for nuclear production plant *(Major only)* |

#### C. Hydraulic Production

| Account | Description |
|---------|-------------|
| 330 | Land and land rights |
| 331 | Structures and improvements |
| 332 | Reservoirs, dams, and waterways |
| 333 | Water wheels, turbines and generators |
| 334 | Accessory electric equipment |
| 335 | Miscellaneous power plant equipment |
| 336 | Roads, railroads and bridges |
| 337 | Asset retirement costs for hydraulic production plant |

#### D. Other Production

| Account | Description |
|---------|-------------|
| 340 | Land and land rights |
| 341 | Structures and improvements |
| 342 | Fuel holders, producers, and accessories |
| 343 | Prime movers |
| 344 | Generators |
| 345 | Accessory electric equipment |
| 346 | Miscellaneous power plant equipment |
| 347 | Asset retirement costs for other production plant |

### 3. Transmission Plant

| Account | Description |
|---------|-------------|
| 350 | Land and land rights |
| 351 | [Reserved] |
| 352 | Structures and improvements |
| 353 | Station equipment |
| 354 | Towers and fixtures |
| 355 | Poles and fixtures |
| 356 | Overhead conductors and devices |
| 357 | Underground conduit |
| 358 | Underground conductors and devices |
| 359 | Roads and trails |
| 359.1 | Asset retirement costs for transmission plant |

### 4. Distribution Plant

| Account | Description |
|---------|-------------|
| 360 | Land and land rights |
| 361 | Structures and improvements |
| 362 | Station equipment |
| 363 | Storage battery equipment |
| 364 | Poles, towers and fixtures |
| 365 | Overhead conductors and devices |
| 366 | Underground conduit |
| 367 | Underground conductors and devices |
| 368 | Line transformers |
| 369 | Services |
| 370 | Meters |
| 371 | Installations on customers' premises |
| 372 | Leased property on customers' premises |
| 373 | Street lighting and signal systems |
| 374 | Asset retirement costs for distribution plant |

### 5. Regional Transmission and Market Operation Plant

| Account | Description |
|---------|-------------|
| 380 | Land and land rights |
| 381 | Structures and improvements |
| 382 | Computer hardware |
| 383 | Computer software |
| 384 | Communication equipment |
| 385 | Miscellaneous regional transmission and market operation plant |
| 386 | Asset retirement costs for regional transmission and market operation plant |
| 387 | [Reserved] |

### 6. General Plant

| Account | Description |
|---------|-------------|
| 389 | Land and land rights |
| 390 | Structures and improvements |
| 391 | Office furniture and equipment |
| 392 | Transportation equipment |
| 393 | Stores equipment |
| 394 | Tools, shop and garage equipment |
| 395 | Laboratory equipment |
| 396 | Power operated equipment |
| 397 | Communication equipment |
| 398 | Miscellaneous equipment |
| 399 | Other tangible property |
| 399.1 | Asset retirement costs for general plant |

## Operating Revenue Chart of Accounts (Account 400)

### 1. Utility Operating Income

| Account | Description |
|---------|-------------|
| 400 | Operating revenues |
| 401 | Operation expense |
| 402 | Maintenance expense |
| 403 | Depreciation expense |
| 404 | Amortization of limited-term electric plant |
| 405 | Amortization of other electric plant |
| 406 | Amortization of electric plant acquisition adjustments |
| 407 | Amortization of property losses, unrecovered plant and regulatory study costs |
| 407.3 | Regulatory debits |
| 407.4 | Regulatory credits |
| 408 | [Reserved] |
| 408.1 | Taxes other than income taxes, utility operating income |
| 409 | [Reserved] |
| 409.1 | Income taxes, utility operating income |
| 410 | [Reserved] |
| 410.1 | Provisions for deferred income taxes, utility operating income |
| 411 | [Reserved] |
| 411.1 | Provision for deferred income taxes — Credit, utility operating income |
| 411.3 | [Reserved] |
| 411.4 | Investment tax credit adjustments, utility operations |
| 411.6 | Gains from disposition of utility plant |
| 411.7 | Losses from disposition of utility plant |
| 411.8 | Gains from disposition of allowances |
| 411.9 | Losses from disposition of allowances |
| 412 | Revenues from electric plant leased to others |
| 413 | Expenses of electric plant leased to others |
| 414 | Other utility operating income |

### 2. Other Income and Deductions

#### A. Other Income

| Account | Description |
|---------|-------------|
| 415 | Revenues from merchandising, jobbing, and contract work |
| 416 | Costs and expenses of merchandising, jobbing, and contract work |
| 417 | Revenues from nonutility operations |
| 417.1 | Expenses of nonutility operations |
| 418 | Nonoperating rental income |
| 418.1 | Equity in earnings of subsidiary companies *(Major only)* |
| 419 | Interest and dividend income |
| 419.1 | Allowance for other funds used during construction |
| 420 | Investment tax credits |
| 421 | Miscellaneous nonoperating income |
| 421.1 | Gain on disposition of property |

#### B. Other Income Deductions

| Account | Description |
|---------|-------------|
| 421.2 | Loss on disposition of property |
| 425 | Miscellaneous amortization |
| 426 | [Reserved] |
| 426.1 | Donations |
| 426.2 | Life insurance |
| 426.3 | Penalties |
| 426.4 | Expenditures for certain civic, political and related activities |
| 426.5 | Other deductions |

#### C. Taxes Applicable to Other Income and Deductions

| Account | Description |
|---------|-------------|
| 408.2 | Taxes other than income taxes, other income and deductions |
| 409.2 | Income tax, other income and deductions |
| 409.3 | Income taxes, extraordinary items |
| 410.2 | Provision for deferred income taxes, other income and deductions |
| 411.2 | Provision for deferred income taxes — Credit, other income and deductions |
| 411.5 | Investment tax credit adjustments, nonutility operations |
| 420 | Investment tax credits |

### 3. Interest Charges

| Account | Description |
|---------|-------------|
| 427 | Interest on long-term debt |
| 428 | Amortization of debt discount and expense |
| 428.1 | Amortization of loss on reacquired debt |
| 429 | Amortization of premium on debt — Cr. |
| 429.1 | Amortization of gain on reacquired debt — Credit |
| 430 | Interest on debt to associated companies |
| 431 | Other interest expense |
| 432 | Allowance for borrowed funds used during construction — Credit |

### 4. Extraordinary Items

| Account | Description |
|---------|-------------|
| 434 | Extraordinary income |
| 435 | Extraordinary deductions |

## Sales of Electricity Chart of Accounts (Account 400, sub-accounts)

### 1. Sales of Electricity

| Account | Description |
|---------|-------------|
| 440 | Residential sales |
| 442 | Commercial and industrial sales |
| 444 | Public street and highway lighting |
| 445 | Other sales to public authorities *(Major only)* |
| 446 | Sales to railroads and railways *(Major only)* |
| 447 | Sales for resale |
| 448 | Interdepartmental sales |
| 449 | Other sales *(Nonmajor only)* |
| 449.1 | Provision for rate refunds |

### 2. Other Operating Revenues

| Account | Description |
|---------|-------------|
| 450 | Forfeited discounts |
| 451 | Miscellaneous service revenues |
| 453 | Sales of water and water power |
| 454 | Rent from electric property |
| 455 | Interdepartmental rents |
| 456 | Other electric revenues |
| 456.1 | Revenues from transmission of electricity of others |
| 457.1 | Regional transmission service revenues |
| 457.2 | Miscellaneous revenues |

## Operation and Maintenance Expense Chart of Accounts

### 1. Power Production Expenses

#### A. Steam Power Generation

##### Operation

| Account | Description |
|---------|-------------|
| 500 | Operation supervision and engineering |
| 501 | Fuel |
| 502 | Steam expenses *(Major only)* |
| 503 | Steam from other sources |
| 504 | Steam transferred — Credit |
| 505 | Electric expenses *(Major only)* |
| 506 | Miscellaneous steam power expenses *(Major only)* |
| 507 | Rents |
| 508 | Operation supplies and expenses *(Nonmajor only)* |
| 509 | Allowances |

##### Maintenance

| Account | Description |
|---------|-------------|
| 510 | Maintenance supervision and engineering *(Major only)* |
| 511 | Maintenance of structures *(Major only)* |
| 512 | Maintenance of boiler plant *(Major only)* |
| 513 | Maintenance of electric plant *(Major only)* |
| 514 | Maintenance of miscellaneous steam plant *(Major only)* |
| 515 | Maintenance of steam production plant *(Nonmajor only)* |

#### B. Nuclear Power Generation

##### Operation

| Account | Description |
|---------|-------------|
| 517 | Operation supervision and engineering *(Major only)* |
| 518 | Nuclear fuel expense *(Major only)* |
| 519 | Coolants and water *(Major only)* |
| 520 | Steam expenses *(Major only)* |
| 521 | Steam from other sources *(Major only)* |
| 522 | Steam transferred — Credit *(Major only)* |
| 523 | Electric expenses *(Major only)* |
| 524 | Miscellaneous nuclear power expenses *(Major only)* |
| 525 | Rents *(Major only)* |

##### Maintenance

| Account | Description |
|---------|-------------|
| 528 | Maintenance supervision and engineering *(Major only)* |
| 529 | Maintenance of structures *(Major only)* |
| 530 | Maintenance of reactor plant equipment *(Major only)* |
| 531 | Maintenance of electric plant *(Major only)* |
| 532 | Maintenance of miscellaneous nuclear plant *(Major only)* |

#### C. Hydraulic Power Generation

##### Operation

| Account | Description |
|---------|-------------|
| 535 | Operation supervision and engineering |
| 536 | Water for power |
| 537 | Hydraulic expenses *(Major only)* |
| 538 | Electric expenses *(Major only)* |
| 539 | Miscellaneous hydraulic power generation expenses *(Major only)* |
| 540 | Rents |
| 540.1 | Operation supplies and expenses *(Nonmajor only)* |

##### Maintenance

| Account | Description |
|---------|-------------|
| 541 | Maintenance supervision and engineering *(Major only)* |
| 542 | Maintenance of structures *(Major only)* |
| 543 | Maintenance of reservoirs, dams and waterways *(Major only)* |
| 544 | Maintenance of electric plant *(Major only)* |
| 545 | Maintenance of miscellaneous hydraulic plant *(Major only)* |
| 545.1 | Maintenance of hydraulic production plant *(Nonmajor only)* |

#### D. Other Power Generation

##### Operation

| Account | Description |
|---------|-------------|
| 546 | Operation supervision and engineering |
| 547 | Fuel |
| 548 | Generation expenses *(Major only)* |
| 549 | Miscellaneous other power generation expenses *(Major only)* |
| 550 | Rents |
| 550.1 | Operation supplies and expenses *(Nonmajor only)* |

##### Maintenance

| Account | Description |
|---------|-------------|
| 551 | Maintenance supervision and engineering *(Major only)* |
| 552 | Maintenance of structures *(Major only)* |
| 553 | Maintenance of generating and electric plant *(Major only)* |
| 554 | Maintenance of miscellaneous other power generation plant *(Major only)* |
| 554.1 | Maintenance of other power production plant *(Nonmajor only)* |

#### E. Other Power Supply Expenses

| Account | Description |
|---------|-------------|
| 555 | Purchased power |
| 556 | System control and load dispatching *(Major only)* |
| 557 | Other expenses |

### 2. Transmission Expenses

#### Operation

| Account | Description |
|---------|-------------|
| 560 | Operation supervision and engineering |
| 561.1 | Load dispatch — Reliability |
| 561.2 | Load dispatch — Monitor and operate transmission system |
| 561.3 | Load dispatch — Transmission service and scheduling |
| 561.4 | Scheduling, system control and dispatch services |
| 561.5 | Reliability planning and standards development |
| 561.6 | Transmission service studies |
| 561.7 | Generation interconnection studies |
| 561.8 | Reliability planning and standards development services |
| 562 | Station expenses *(Major only)* |
| 563 | Overhead line expenses *(Major only)* |
| 564 | Underground line expenses *(Major only)* |
| 565 | Transmission of electricity by others *(Major only)* |
| 566 | Miscellaneous transmission expenses *(Major only)* |
| 567 | Rents |
| 567.1 | Operation supplies and expenses *(Nonmajor only)* |

#### Maintenance

| Account | Description |
|---------|-------------|
| 568 | Maintenance supervision and engineering *(Major only)* |
| 569 | Maintenance of structures *(Major only)* |
| 569.1 | Maintenance of computer hardware |
| 569.2 | Maintenance of computer software |
| 569.3 | Maintenance of communication equipment |
| 569.4 | Maintenance of miscellaneous regional transmission plant |
| 570 | Maintenance of station equipment *(Major only)* |
| 571 | Maintenance of overhead lines *(Major only)* |
| 572 | Maintenance of underground lines *(Major only)* |
| 573 | Maintenance of miscellaneous transmission plant *(Major only)* |
| 574 | Maintenance of transmission plant *(Nonmajor only)* |

### 3. Regional Market Expenses

#### Operation

| Account | Description |
|---------|-------------|
| 575.1 | Operation supervision |
| 575.2 | Day-ahead and real-time market administration |
| 575.3 | Transmission rights market administration |
| 575.4 | Capacity market administration |
| 575.5 | Ancillary services market administration |
| 575.6 | Market monitoring and compliance |
| 575.7 | Market administration, monitoring and compliance services |
| 575.8 | Rents |

#### Maintenance

| Account | Description |
|---------|-------------|
| 576.1 | Maintenance of structures and improvements |
| 576.2 | Maintenance of computer hardware |
| 576.3 | Maintenance of computer software |
| 576.4 | Maintenance of communication equipment |
| 576.5 | Maintenance of miscellaneous market operation plant |

### 4. Distribution Expenses

#### Operation

| Account | Description |
|---------|-------------|
| 580 | Operation supervision and engineering |
| 581 | Load dispatching *(Major only)* |
| 581.1 | Line and station expenses *(Nonmajor only)* |
| 582 | Station expenses *(Major only)* |
| 583 | Overhead line expenses *(Major only)* |
| 584 | Underground line expenses *(Major only)* |
| 585 | Street lighting and signal system expenses |
| 586 | Meter expenses |
| 587 | Customer installations expenses |
| 588 | Miscellaneous distribution expenses |
| 589 | Rents |

#### Maintenance

| Account | Description |
|---------|-------------|
| 590 | Maintenance supervision and engineering *(Major only)* |
| 591 | Maintenance of structures *(Major only)* |
| 592 | Maintenance of station equipment *(Major only)* |
| 592.1 | Maintenance of structures and equipment *(Nonmajor only)* |
| 593 | Maintenance of overhead lines *(Major only)* |
| 594 | Maintenance of underground lines *(Major only)* |
| 594.1 | Maintenance of lines *(Nonmajor only)* |
| 595 | Maintenance of line transformers |
| 596 | Maintenance of street lighting and signal systems |
| 597 | Maintenance of meters |
| 598 | Maintenance of miscellaneous distribution plant |

### 5. Customer Accounts Expenses

#### Operation

| Account | Description |
|---------|-------------|
| 901 | Supervision *(Major only)* |
| 902 | Meter reading expenses |
| 903 | Customer records and collection expenses |
| 904 | Uncollectible accounts |
| 905 | Miscellaneous customer accounts expenses *(Major only)* |

### 6. Customer Service and Informational Expenses

#### Operation

| Account | Description |
|---------|-------------|
| 906 | Customer service and informational expenses *(Nonmajor only)* |
| 907 | Supervision *(Major only)* |
| 908 | Customer assistance expenses *(Major only)* |
| 909 | Informational and instructional advertising expenses *(Major only)* |
| 910 | Miscellaneous customer service and informational expenses *(Major only)* |

### 7. Sales Expenses

#### Operation

| Account | Description |
|---------|-------------|
| 911 | Supervision *(Major only)* |
| 912 | Demonstrating and selling expenses *(Major only)* |
| 913 | Advertising expenses *(Major only)* |
| 914 | Revenues from merchandising, jobbing and contract work |
| 915 | Cost and expenses of merchandising, jobbing and contract work |
| 916 | Miscellaneous sales expenses *(Major only)* |
| 917 | Sales expenses *(Nonmajor only)* |

### 8. Administrative and General Expenses

#### Operation

| Account | Description |
|---------|-------------|
| 920 | Administrative and general salaries |
| 921 | Office supplies and expenses |
| 922 | Administrative expenses transferred — Credit |
| 923 | Outside services employed |
| 924 | Property insurance |
| 925 | Injuries and damages |
| 926 | Employee pensions and benefits |
| 927 | Franchise requirements |
| 928 | Regulatory commission expenses |
| 929 | Duplicate charges — Credit |
| 930.1 | General advertising expenses |
| 930.2 | Miscellaneous general expenses |
| 931 | Rents |
| 933 | Transportation expenses *(Nonmajor only)* |

#### Maintenance

| Account | Description |
|---------|-------------|
| 935 | Maintenance of general plant |

<!-- END GENERATED CONTENT -->
