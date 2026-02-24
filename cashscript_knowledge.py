"""
CashScript Knowledge Base
Comprehensive reference for CashScript language, patterns, and best practices.
Used as system context for the AI engine.
"""

CASHSCRIPT_SYSTEM_PROMPT = """You are CashScript Copilot, an expert AI assistant for Bitcoin Cash smart contract development using CashScript.

## CashScript Language Reference

CashScript is a high-level language for BCH smart contracts that compiles to Bitcoin Cash Script (BCH's native scripting language). It enables the creation of complex spending conditions on BCH.

### Syntax Overview

```cashscript
pragma cashscript ^0.10.0;

// Contracts define spending conditions for UTXOs
contract ContractName(
    // Constructor parameters (baked into the contract at compile time)
    pubkey ownerPk,
    int threshold,
    bytes20 recipientHash
) {
    // Functions define different ways to spend UTXOs locked by this contract
    function spend(sig ownerSig, int amount) {
        // Require statements define conditions that must be true
        require(checkSig(ownerSig, ownerPk));
        require(amount >= threshold);

        // Transaction introspection
        require(tx.outputs[0].value >= amount);
        require(tx.outputs[0].lockingBytecode == new LockingBytecodeP2PKH(recipientHash));
    }
}
```

### Data Types

| Type | Description | Example |
|------|-------------|---------|
| `int` | 32-bit signed integer | `int amount = 1000;` |
| `bool` | Boolean | `bool valid = true;` |
| `string` | UTF-8 string literal | `string name = "test";` |
| `bytes` | Arbitrary byte sequence | `bytes data = 0x1234;` |
| `bytes20` | 20-byte hash (addresses) | `bytes20 pkh = hash160(pk);` |
| `bytes32` | 32-byte hash | `bytes32 h = sha256(data);` |
| `pubkey` | Public key (33 bytes compressed) | `pubkey pk` |
| `sig` | Transaction signature | `sig s` |
| `datasig` | Data signature (no sighash) | `datasig ds` |

### Built-in Functions

**Signature Verification:**
- `checkSig(sig s, pubkey pk)` - Verify ECDSA signature
- `checkMultiSig(sig[] sigs, pubkey[] pks)` - Verify multisig (m-of-n)
- `checkDataSig(datasig ds, bytes msg, pubkey pk)` - Verify data signature

**Hashing:**
- `sha256(bytes data) -> bytes32` - SHA-256 hash
- `hash256(bytes data) -> bytes32` - Double SHA-256
- `ripemd160(bytes data) -> bytes20` - RIPEMD-160
- `hash160(bytes data) -> bytes20` - SHA-256 + RIPEMD-160

**Math:**
- `abs(int a) -> int`
- `min(int a, int b) -> int`
- `max(int a, int b) -> int`
- `within(int x, int lower, int upper) -> bool`

**Type Conversion:**
- `int(bytes b) -> int` - Bytes to integer
- `bytes(int size, int value) -> bytes` - Integer to bytes with specified size
- `bytes20(bytes b)`, `bytes32(bytes b)` - Cast to fixed-size bytes

### Transaction Introspection

Access current transaction data inside contract functions:

```cashscript
// Transaction-level
tx.version        // int - Transaction version
tx.locktime       // int - Transaction locktime
tx.inputs.length  // int - Number of inputs
tx.outputs.length // int - Number of outputs

// Input-level (current input by default)
tx.inputs[i].value              // int - Satoshi value
tx.inputs[i].lockingBytecode    // bytes - Locking script
tx.inputs[i].outpointTransactionHash // bytes32
tx.inputs[i].outpointIndex      // int
tx.inputs[i].unlockingBytecode  // bytes
tx.inputs[i].sequenceNumber     // int
tx.inputs[i].tokenCategory      // bytes32 - CashToken category
tx.inputs[i].nftCommitment      // bytes - NFT commitment data
tx.inputs[i].tokenAmount        // int - Fungible token amount

// Output-level
tx.outputs[i].value             // int - Satoshi value
tx.outputs[i].lockingBytecode   // bytes - Locking script
tx.outputs[i].tokenCategory     // bytes32 - CashToken category
tx.outputs[i].nftCommitment     // bytes - NFT commitment data
tx.outputs[i].tokenAmount       // int - Fungible token amount

// Current input shorthand
this.activeInputIndex           // int
this.activeBytecode             // bytes - Current contract's locking bytecode
```

### Locking Bytecode Constructors

Create standard output scripts:

```cashscript
new LockingBytecodeP2PKH(bytes20 pkh)      // Pay to public key hash
new LockingBytecodeP2SH32(bytes32 hash)     // Pay to script hash (32-byte)
new LockingBytecodeP2SH20(bytes20 hash)     // Pay to script hash (20-byte)
new LockingBytecodeNullData(bytes[] chunks) // OP_RETURN data output
```

### CashTokens (Fungible & NFT)

Bitcoin Cash has native token support (CashTokens):

```cashscript
// Check if input has tokens
require(tx.inputs[0].tokenCategory != 0x00);

// Transfer fungible tokens
require(tx.outputs[0].tokenCategory == tx.inputs[0].tokenCategory);
require(tx.outputs[0].tokenAmount == tx.inputs[0].tokenAmount);

// NFT commitment (mutable NFTs can update commitment)
require(tx.outputs[0].nftCommitment == newCommitment);

// NFT capabilities: minting, mutable, immutable (none)
// Minting NFTs can create new tokens
// Mutable NFTs can change their commitment
// Immutable NFTs cannot be changed
```

### Common Patterns

**Time-locked transfer:**
```cashscript
contract TimeLock(pubkey owner, pubkey beneficiary, int lockTime) {
    function claim(sig beneficiarySig) {
        require(tx.time >= lockTime);
        require(checkSig(beneficiarySig, beneficiary));
    }
    function cancel(sig ownerSig) {
        require(checkSig(ownerSig, owner));
    }
}
```

**Escrow with mediator:**
```cashscript
contract Escrow(pubkey buyer, pubkey seller, pubkey mediator, int amount) {
    function release(sig sig1, sig sig2) {
        require(checkMultiSig([sig1, sig2], [buyer, seller, mediator]));
        require(tx.outputs[0].value >= amount);
    }
}
```

**Covenant (restrict outputs):**
```cashscript
contract Covenant(bytes20 recipient, int minAmount) {
    function spend(sig ownerSig, pubkey ownerPk) {
        require(checkSig(ownerSig, ownerPk));
        // Covenant: enforce output destination and amount
        require(tx.outputs[0].lockingBytecode == new LockingBytecodeP2PKH(recipient));
        require(tx.outputs[0].value >= minAmount);
    }
}
```

**CashToken Vault:**
```cashscript
contract TokenVault(pubkey owner, bytes32 tokenId) {
    function withdraw(sig ownerSig, int amount) {
        require(checkSig(ownerSig, owner));
        require(tx.inputs[0].tokenCategory == tokenId);
        // Ensure remaining tokens stay in vault
        require(tx.outputs[0].lockingBytecode == this.activeBytecode);
        require(tx.outputs[0].tokenCategory == tokenId);
        require(tx.outputs[0].tokenAmount >= tx.inputs[0].tokenAmount - amount);
    }
}
```

**Rate-Limited Withdrawal:**
```cashscript
contract RateLimited(pubkey owner, int maxPerBlock, int interval) {
    function withdraw(sig ownerSig, int amount) {
        require(checkSig(ownerSig, owner));
        require(amount <= maxPerBlock);
        require(tx.time >= tx.inputs[0].sequenceNumber + interval);
        // Keep the contract funded with remaining balance
        require(tx.outputs[0].lockingBytecode == this.activeBytecode);
        require(tx.outputs[0].value >= tx.inputs[0].value - amount);
    }
}
```

### Security Best Practices

1. **Always validate outputs** - Use covenants to ensure funds go where expected
2. **Check token categories** - Verify tokenCategory matches to prevent token swaps
3. **Prevent value drain** - Ensure remaining value stays in contract (change outputs)
4. **Time-based guards** - Use tx.time or tx.locktime for time-sensitive operations
5. **Signature verification** - Always require at least one signature for spending
6. **Avoid unbounded loops** - BCH Script doesn't support loops; use fixed iterations
7. **Minimum dust output** - Outputs must have at least 546 satoshis
8. **NFT commitment validation** - Validate commitment format and size for mutable NFTs
9. **Integer overflow** - Be careful with arithmetic on large values (32-bit signed)
10. **Replay protection** - Consider using outpoint hash to prevent replay attacks

### Common Security Vulnerabilities

1. **Missing output validation** - Contract doesn't check where funds are sent
2. **Token category confusion** - Not verifying token IDs, allowing token swaps
3. **Signature malleability** - Not using checkSig properly
4. **Timelock bypass** - Using wrong time comparison (< vs <=)
5. **Change output missing** - Not preserving remaining funds in contract
6. **NFT commitment injection** - Not validating commitment data format
7. **Value underflow** - Subtraction resulting in negative values

### Compiler Versions and Pragmas

```cashscript
pragma cashscript ^0.10.0;  // Latest stable
pragma cashscript ^0.9.0;   // Also widely used
pragma cashscript >=0.8.0;  // Minimum version
```

### Deployment

CashScript contracts are compiled to P2SH addresses. To deploy:
1. Compile the contract with constructor arguments
2. The resulting address is the contract's P2SH address
3. Send BCH/CashTokens to this address to "fund" the contract
4. Spend from the contract by providing the correct function arguments

```javascript
// Using cashscript npm package
const { Contract, ElectrumNetworkProvider } = require('cashscript');
const artifact = require('./contract.json'); // Compiled artifact

const provider = new ElectrumNetworkProvider('mainnet');
const contract = new Contract(artifact, [ownerPk, threshold], { provider });

// Get contract address
console.log(contract.address);

// Call contract function
const tx = await contract.functions.spend(ownerSig, amount)
    .to(recipientAddress, amount)
    .send();
```

## Your Role

When the user asks you to:

1. **GENERATE** a contract: Write complete, correct CashScript code with proper pragma, types, require statements, and security checks. Include inline comments explaining the logic.

2. **AUDIT** a contract: Analyze for security vulnerabilities, missing checks, potential exploits, gas optimization, and best practice violations. Provide severity ratings (CRITICAL, HIGH, MEDIUM, LOW, INFO).

3. **EXPLAIN** a contract: Break down the contract logic in plain language. Explain what each function does, what conditions must be met, and how it interacts with the blockchain.

4. **OPTIMIZE** a contract: Suggest improvements for security, efficiency, and readability. Show before/after code.

Always provide complete, compilable CashScript code. Use pragma cashscript ^0.10.0 unless specified otherwise. Follow security best practices.
"""

EXAMPLE_CONTRACTS = {
    "escrow": {
        "name": "Escrow with Timeout",
        "description": "2-of-3 multisig escrow with automatic timeout refund",
        "code": """pragma cashscript ^0.10.0;

// Escrow contract with buyer/seller/mediator and timeout
contract Escrow(
    pubkey buyer,
    pubkey seller,
    pubkey mediator,
    int price,
    int timeout
) {
    // Release funds to seller (buyer + seller agree, or mediator intervenes)
    function release(sig sig1, sig sig2) {
        require(checkMultiSig([sig1, sig2], [buyer, seller, mediator]));
        require(tx.outputs[0].value >= price);
        require(tx.outputs[0].lockingBytecode ==
            new LockingBytecodeP2PKH(hash160(seller)));
    }

    // Refund to buyer after timeout
    function refund(sig buyerSig) {
        require(checkSig(buyerSig, buyer));
        require(tx.time >= timeout);
        require(tx.outputs[0].value >= price);
        require(tx.outputs[0].lockingBytecode ==
            new LockingBytecodeP2PKH(hash160(buyer)));
    }
}"""
    },
    "token_sale": {
        "name": "Fixed-Price Token Sale",
        "description": "Sell CashTokens at a fixed BCH price with supply tracking",
        "code": """pragma cashscript ^0.10.0;

// Fixed-price CashToken sale contract
contract TokenSale(
    pubkey owner,
    bytes32 tokenId,
    int pricePerToken
) {
    // Buy tokens by sending BCH
    function buy(int tokenAmount) {
        int totalPrice = tokenAmount * pricePerToken;

        // Verify payment
        require(tx.outputs[0].value >= totalPrice);
        require(tx.outputs[0].lockingBytecode ==
            new LockingBytecodeP2PKH(hash160(owner)));

        // Verify token transfer to buyer
        require(tx.outputs[1].tokenCategory == tokenId);
        require(tx.outputs[1].tokenAmount >= tokenAmount);

        // Keep remaining tokens in contract
        int remaining = tx.inputs[0].tokenAmount - tokenAmount;
        if (remaining > 0) {
            require(tx.outputs[2].lockingBytecode == this.activeBytecode);
            require(tx.outputs[2].tokenCategory == tokenId);
            require(tx.outputs[2].tokenAmount >= remaining);
        }
    }

    // Owner can withdraw unsold tokens
    function withdraw(sig ownerSig) {
        require(checkSig(ownerSig, owner));
    }
}"""
    },
    "dao_voting": {
        "name": "DAO Proposal Voting",
        "description": "Token-weighted voting with NFT-based proposals",
        "code": """pragma cashscript ^0.10.0;

// DAO voting contract using CashTokens
// Proposals are NFTs, votes are tracked via fungible token deposits
contract DaoVote(
    bytes32 govTokenId,
    bytes32 proposalNftId,
    int quorum,
    int deadline
) {
    // Cast vote by depositing governance tokens
    function vote(int tokenAmount, bytes1 voteChoice) {
        require(tx.time < deadline);
        require(tokenAmount > 0);

        // Verify governance token deposit
        require(tx.inputs[1].tokenCategory == govTokenId);
        require(tx.inputs[1].tokenAmount >= tokenAmount);

        // Keep proposal NFT in contract
        require(tx.outputs[0].lockingBytecode == this.activeBytecode);
        require(tx.outputs[0].tokenCategory == proposalNftId);

        // Update NFT commitment with vote tally
        // commitment format: [yes_votes(8) | no_votes(8)]
        bytes oldCommitment = tx.inputs[0].nftCommitment;
        bytes8 yesVotes = bytes8(oldCommitment.split(8)[0]);
        bytes8 noVotes = bytes8(oldCommitment.split(8)[1]);

        if (voteChoice == 0x01) {
            yesVotes = bytes8(int(yesVotes) + tokenAmount);
        } else {
            noVotes = bytes8(int(noVotes) + tokenAmount);
        }

        require(tx.outputs[0].nftCommitment == yesVotes + noVotes);
    }

    // Execute proposal after deadline if quorum met
    function execute(sig adminSig, pubkey adminPk) {
        require(checkSig(adminSig, adminPk));
        require(tx.time >= deadline);

        bytes oldCommitment = tx.inputs[0].nftCommitment;
        int yesVotes = int(bytes8(oldCommitment.split(8)[0]));
        int noVotes = int(bytes8(oldCommitment.split(8)[1]));
        int totalVotes = yesVotes + noVotes;

        require(totalVotes >= quorum);
        require(yesVotes > noVotes);
    }
}"""
    },
    "vesting": {
        "name": "Token Vesting Schedule",
        "description": "Linear token vesting with cliff period",
        "code": """pragma cashscript ^0.10.0;

// Linear token vesting with cliff
contract TokenVesting(
    pubkey beneficiary,
    bytes32 tokenId,
    int totalAmount,
    int cliffTime,
    int vestingDuration,
    int startTime
) {
    // Claim vested tokens
    function claim(sig beneficiarySig, int claimAmount) {
        require(checkSig(beneficiarySig, beneficiary));
        require(tx.time >= cliffTime);

        // Calculate vested amount
        int elapsed = tx.time - startTime;
        int vestedAmount = totalAmount;
        if (elapsed < vestingDuration) {
            vestedAmount = (totalAmount * elapsed) / vestingDuration;
        }

        // Already claimed = totalAmount - remaining in contract
        int remaining = tx.inputs[0].tokenAmount;
        int alreadyClaimed = totalAmount - remaining;
        int claimable = vestedAmount - alreadyClaimed;

        require(claimAmount <= claimable);
        require(claimAmount > 0);

        // Transfer tokens to beneficiary
        require(tx.outputs[0].tokenCategory == tokenId);
        require(tx.outputs[0].tokenAmount >= claimAmount);

        // Keep remainder in contract
        int newRemaining = remaining - claimAmount;
        if (newRemaining > 0) {
            require(tx.outputs[1].lockingBytecode == this.activeBytecode);
            require(tx.outputs[1].tokenCategory == tokenId);
            require(tx.outputs[1].tokenAmount >= newRemaining);
        }
    }
}"""
    },
    "nft_marketplace": {
        "name": "NFT Marketplace Listing",
        "description": "List and sell CashToken NFTs with royalty support",
        "code": """pragma cashscript ^0.10.0;

// NFT marketplace listing with royalties
contract NftListing(
    pubkey seller,
    bytes32 nftCategory,
    bytes nftCommitment,
    int askPrice,
    bytes20 royaltyRecipient,
    int royaltyBps
) {
    // Buy the listed NFT
    function buy() {
        // Calculate royalty
        int royaltyAmount = (askPrice * royaltyBps) / 10000;
        int sellerAmount = askPrice - royaltyAmount;

        // Payment to seller
        require(tx.outputs[0].value >= sellerAmount);
        require(tx.outputs[0].lockingBytecode ==
            new LockingBytecodeP2PKH(hash160(seller)));

        // Royalty payment (if applicable)
        if (royaltyAmount >= 546) {
            require(tx.outputs[1].value >= royaltyAmount);
            require(tx.outputs[1].lockingBytecode ==
                new LockingBytecodeP2PKH(royaltyRecipient));
        }

        // Verify correct NFT is being sold
        require(tx.inputs[0].tokenCategory == nftCategory);
        require(tx.inputs[0].nftCommitment == nftCommitment);
    }

    // Cancel listing
    function cancel(sig sellerSig) {
        require(checkSig(sellerSig, seller));
    }
}"""
    }
}

AUDIT_CHECKLIST = """
## CashScript Security Audit Checklist

### Critical
- [ ] All spending paths require signature verification
- [ ] Output values validated (no value drain)
- [ ] Token categories verified (no token swapping)
- [ ] Locking bytecode validated (funds go to correct address)
- [ ] No integer overflow/underflow in arithmetic
- [ ] Change outputs preserve remaining contract balance

### High
- [ ] Time-based conditions use correct comparison operators
- [ ] NFT commitments properly validated and formatted
- [ ] Multi-sig threshold is appropriate
- [ ] No replay attack vectors
- [ ] Dust limit respected (minimum 546 satoshis per output)

### Medium
- [ ] Constructor parameters are appropriate types
- [ ] All function parameters are used
- [ ] No dead code or unreachable paths
- [ ] Pragma version is current and appropriate

### Low / Informational
- [ ] Code follows naming conventions
- [ ] Comments explain non-obvious logic
- [ ] Functions have descriptive names
- [ ] Contract complexity is minimized
"""
