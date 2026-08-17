# Coffee Chat Guide

## The Story You Should Tell Yourself

You are not walking into this chat to prove that the platform is bad or that the leader is weak.

You are walking in to answer a more useful question: is this a place where the people in charge understand what they built, why they built it, and whether it can evolve sensibly?

That means your goal is to collect signal, not to win an argument.

You want to learn:

- what problem the platform is actually solving
- whether the design choices were intentional
- whether the team understands tradeoffs
- whether the architecture allows reasonable change
- whether this org would give you room to do sensible engineering

## The Mindset

Go in with:

- curiosity
- calm
- operational language
- no need to prove anything

This matters because if you sound like you are auditing them, they will defend. If you sound like you are trying to understand, they will reveal more.

## Step-By-Step Guideline

### Step 1: Start Broad

Start with the platform purpose, not the flaws.

Use a question like:

> Could you walk me through what problem the platform was meant to solve and how you think about its role in the broader stack?

### Why This Matters

If they cannot explain the purpose clearly, almost everything else is downstream noise.

You are checking whether the platform has:

- a real problem statement
- a clear role
- a bounded scope

### What To Watch For

Good signs:

- a concrete problem statement
- specific users or teams
- clear boundaries

Warning signs:

- vague mission language
- buzzwords replacing explanation
- no clear definition of where the platform starts and ends

### Step 2: Understand Users and Boundaries

Once they explain the platform, move to who it serves and what belongs inside it.

Ask:

> Who are the main users or teams this platform serves?

> What decisions belong in the platform versus in feature or product teams?

### Why This Matters

Many weak platforms become weak because they try to own everything.

You are checking whether they understand:

- customer or internal user needs
- ownership boundaries
- division of responsibility

### What To Watch For

Good signs:

- named user groups
- clear ownership lines
- a sensible boundary between platform and feature work

Warning signs:

- everything gets centralized
- ownership is fuzzy
- platform scope sounds elastic and political

### Step 3: Probe Operational Friction

Now move into something concrete and neutral: onboarding time.

Ask:

> I noticed onboarding seems to take around three weeks. What are the main steps driving that timeline, and which parts are essential versus historical process?

Follow with:

> If you wanted to shorten onboarding significantly, where are the main bottlenecks?

### Why This Matters

This is a practical test. It shows whether they understand where complexity comes from and whether they think in terms of improvement loops.

### What To Watch For

Good signs:

- they can break down the steps clearly
- they know which parts are necessary
- they can name bottlenecks and improvement opportunities

Warning signs:

- "that's just how it works"
- no clear breakdown
- no ownership of the friction

### Step 4: Probe Design Tradeoffs

Move to the OCR and model choices, but frame it as understanding a tradeoff, not criticizing a decision.

Ask:

> I saw the system uses a fairly advanced model, but downstream seems to mainly keep text. How did the team decide on that tradeoff?

Then ask:

> Was the current model chosen mainly for accuracy, future needs, or implementation convenience?

### Why This Matters

This question tests whether the team selected technology because it matched a requirement, or because it sounded powerful.

### What To Watch For

Good signs:

- clear tradeoff reasoning
- awareness of cost, accuracy, and product need
- honest explanation of why capability exceeds current use

Warning signs:

- expensive tooling with no clear downstream benefit
- vague answers like "for flexibility"
- technology choice justified by trend rather than need

### Step 5: Test Architectural Flexibility

Once you understand the current choice, test whether change is possible.

Ask:

> If downstream usage is mostly text, is the OCR layer designed so the model or provider can be swapped based on cost, quality, or document type?

And:

> How tightly coupled is the rest of the pipeline to the current OCR output?

### Why This Matters

You are testing whether the team built an adaptable system or a hard-wired one.

This is not just about OCR. It tells you how they think about abstraction and future change.

### What To Watch For

Good signs:

- the OCR layer is replaceable
- there are interfaces or clean boundaries
- they understand what would break if they swapped providers

Warning signs:

- the implementation is hard-wired
- coupling is accidental and widespread
- no one really knows how expensive change would be

### Step 6: Test Whether Flexibility Is Real

You noticed the system allows custom definitions but the module feels rigid. Ask about that balance directly.

Use:

> I noticed the platform allows custom definitions, but the module structure seems fairly constrained. How do you think about the balance between flexibility and control?

And:

> Is that rigidity intentional, or more a result of how the module evolved?

### Why This Matters

Many systems are described as customizable, but only within a narrow path. You want to know whether the team is intentionally limiting extension or whether the design simply ossified.

### What To Watch For

Good signs:

- clear reasons for the constraints
- known extension points
- honest discussion of limitations

Warning signs:

- claims of flexibility that do not hold up in practice
- defensiveness about rigidity
- inability to explain whether the constraints were deliberate

### Step 7: Ask For Reflection

Close with a question that reveals maturity.

Ask:

> If you were redesigning it today, what would you keep the same, and what would you change?

### Why This Matters

Strong engineers and strong leaders can reflect on what they would do differently. Weak ones often defend everything or answer in generic terms.

### What To Watch For

Good signs:

- honest reflection
- clear priorities
- lessons learned

Warning signs:

- "nothing"
- generic or political answers
- inability to discuss tradeoffs candidly

## The Main Diagnostic Test

At the end, what you really want to know is this:

- do they actually understand their system
- or are they just describing it after the fact

If their answers are concrete, bounded, and tradeoff-aware, that is a good sign even if the design is imperfect.

If their answers are vague, slogan-driven, or defensive, that is the stronger warning sign.

## Reference Table

| Topic | Question to Ask | Your Focus | Good Signs in Reply | Warning Signs in Reply |
|---|---|---|---|---|
| Platform purpose | "Could you walk me through what problem the platform was meant to solve and how you think about its role in the broader stack?" | Is there a real problem definition and clear role? | Clear problem statement, concrete purpose, specific scope | Vague mission, buzzwords, no clear role |
| Users and boundaries | "Who are the main users or teams this platform serves?" "What decisions belong in the platform versus in feature or product teams?" | Is the platform boundary clear? | Named users, clear ownership lines, defined boundaries | Everything belongs to platform, unclear ownership, fuzzy scope |
| Onboarding time | "I noticed onboarding seems to take around three weeks. What are the main steps driving that timeline, and which parts are essential versus historical process?" | Is the complexity justified? | Clear steps, known bottlenecks, awareness of reducible friction | "That's just how it works," no breakdown, no improvement thinking |
| Onboarding optimization | "If you wanted to shorten onboarding significantly, where are the main bottlenecks?" | Do they think in improvement loops? | Specific bottlenecks, realistic improvement ideas | No idea, no ownership of the problem |
| OCR/model choice | "I saw the system uses a fairly advanced model, but downstream seems to mainly keep text. How did the team decide on that tradeoff?" | Was the design intentional? | Clear tradeoff reasoning, accuracy/cost/product rationale | Expensive choice with no clear reason, "because it's advanced" |
| Structured output usage | "Do you see cases where preserving layout or table structure would materially improve later use, or is plain text the real requirement today?" | Do capabilities match real needs? | Clear current requirement, thoughtful future cases | Capability mismatch, hand-wavy "maybe later" justification |
| OCR flexibility | "If downstream usage is mostly text, is the OCR layer designed so the model or provider can be swapped based on cost, quality, or document type?" | Is the architecture adaptable? | Replaceable layer, interface thinking, awareness of coupling | Hard-wired implementation, vendor lock-in by accident |
| OCR coupling | "How tightly coupled is the rest of the pipeline to the current OCR output?" | How expensive is change? | Known dependencies, clear abstraction points | No one knows, change sounds risky everywhere |
| Custom definitions vs rigidity | "I noticed the platform allows custom definitions, but the module structure seems fairly constrained. How do you think about the balance between flexibility and control?" | Is flexibility real or superficial? | Intentional constraints, clear reasons, known extension points | Claims of flexibility that break under real use |
| Source of rigidity | "Is that rigidity intentional, or more a result of how the module evolved?" | Are they self-aware about design debt? | Honest answer, clear tradeoffs, known history | Defensiveness, no ownership, rationalizing legacy choices |
| Future evolution | "If you were redesigning it today, what would you keep the same, and what would you change?" | Can they reflect critically? | Honest reflection, priorities, clear lessons learned | "Nothing," or generic answers with no substance |
