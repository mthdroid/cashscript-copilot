/**
 * CashScript Copilot - On-Chain Proof Deployment
 * Deploys a CashScript contract to BCH chipnet (testnet)
 * and records the transaction ID as hackathon proof.
 *
 * Usage:
 *   cd onchain-proof
 *   npm install
 *   node deploy.js
 */

import { randomBytes } from 'node:crypto';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline';

import { Contract, ElectrumNetworkProvider, SignatureTemplate } from 'cashscript';
import { compileFile } from 'cashc';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─── Crypto setup ──────────────────────────────────────────────────────────

async function getSecp256k1() {
    const lib = await import('@bitauth/libauth');
    // libauth v3: secp256k1 is a direct export
    if (lib.secp256k1 && typeof lib.secp256k1.derivePublicKeyCompressed === 'function') {
        return lib.secp256k1;
    }
    // libauth v2 fallback: need to instantiate
    if (lib.instantiateSecp256k1) {
        return await lib.instantiateSecp256k1();
    }
    throw new Error('Could not initialize secp256k1 from @bitauth/libauth');
}

// ─── Helpers ───────────────────────────────────────────────────────────────

function ask(prompt) {
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    return new Promise(resolve => {
        rl.question(prompt, answer => { rl.close(); resolve(answer); });
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
    console.log('');
    console.log('  ╔═══════════════════════════════════════════════════╗');
    console.log('  ║   CashScript Copilot - On-Chain Proof             ║');
    console.log('  ║   BCH Chipnet (testnet) Deployment                ║');
    console.log('  ╚═══════════════════════════════════════════════════╝');
    console.log('');

    // ── Step 1: Keypair ────────────────────────────────────────────────────
    console.log('[1/5] Setting up keypair...');

    const secp256k1 = await getSecp256k1();
    const keysFile = join(__dirname, 'keys.json');
    let privkey, pubkey;

    if (existsSync(keysFile)) {
        const saved = JSON.parse(readFileSync(keysFile, 'utf8'));
        privkey = new Uint8Array(Buffer.from(saved.privkey, 'hex'));
        pubkey = new Uint8Array(Buffer.from(saved.pubkey, 'hex'));
        console.log('  Loaded existing keys from keys.json');
    } else {
        privkey = new Uint8Array(randomBytes(32));
        const pubkeyResult = secp256k1.derivePublicKeyCompressed(privkey);
        if (typeof pubkeyResult === 'string') {
            throw new Error('Failed to derive public key: ' + pubkeyResult);
        }
        pubkey = pubkeyResult;

        writeFileSync(keysFile, JSON.stringify({
            privkey: Buffer.from(privkey).toString('hex'),
            pubkey: Buffer.from(pubkey).toString('hex'),
            network: 'chipnet',
            generated: new Date().toISOString()
        }, null, 2));
        console.log('  Generated new keypair -> keys.json');
    }

    console.log(`  Pubkey: ${Buffer.from(pubkey).toString('hex').slice(0, 16)}...`);

    // ── Step 2: Compile contract ───────────────────────────────────────────
    console.log('\n[2/5] Compiling contract...');

    const contractPath = join(__dirname, 'contract.cash');
    const artifact = compileFile(contractPath);
    console.log(`  Contract: ${artifact.contractName}`);
    console.log(`  Compiler: cashc`);

    // ── Step 3: Connect to chipnet ─────────────────────────────────────────
    console.log('\n[3/5] Connecting to BCH chipnet...');

    const provider = new ElectrumNetworkProvider('chipnet');
    const contract = new Contract(artifact, [pubkey], { provider });

    console.log(`  Contract address: ${contract.address}`);

    // ── Step 4: Fund the contract ──────────────────────────────────────────
    console.log('\n[4/5] Checking balance...');

    let balance = await contract.getBalance();
    console.log(`  Current balance: ${balance} satoshis`);

    if (balance < 10000n) {
        console.log('');
        console.log('  ┌─────────────────────────────────────────────────┐');
        console.log('  │  CONTRACT NEEDS FUNDING                         │');
        console.log('  │                                                 │');
        console.log(`  │  Address: ${contract.address.slice(0, 45)}...  │`);
        console.log('  │                                                 │');
        console.log('  │  1. Copy the address above                      │');
        console.log('  │  2. Go to: https://tbch.googol.cash/            │');
        console.log('  │  3. Paste address and request tBCH              │');
        console.log('  │  4. Come back here and press Enter              │');
        console.log('  └─────────────────────────────────────────────────┘');
        console.log('');
        console.log(`  Full address: ${contract.address}`);
        console.log('');

        await ask('  Press Enter after funding the contract... ');

        // Poll for balance
        console.log('  Waiting for funds to arrive...');
        let attempts = 0;
        while (balance < 10000n && attempts < 60) {
            await sleep(5000);
            try {
                balance = await contract.getBalance();
            } catch (e) {
                // Network hiccup, retry
            }
            attempts++;
            process.stdout.write(`\r  Checking... ${balance} satoshis (${attempts}/60)`);
        }
        console.log('');

        if (balance < 10000n) {
            console.log('  X Timeout. Run this script again after the faucet confirms.');
            process.exit(1);
        }
    }

    console.log(`  Balance: ${balance} satoshis`);

    // ── Step 5: Execute transaction ────────────────────────────────────────
    console.log('\n[5/5] Sending transaction...');

    try {
        const tx = await contract.functions
            .transfer(new SignatureTemplate(privkey))
            .to(contract.address, 1000n)
            .withOpReturn([
                'CashScript Copilot',
                'BCH-1 Hackcelerator 2026',
                'github.com/mthdroid/cashscript-copilot'
            ])
            .send();

        console.log('');
        console.log('  ╔═══════════════════════════════════════════════════╗');
        console.log('  ║   TRANSACTION SUCCESSFUL                          ║');
        console.log('  ╚═══════════════════════════════════════════════════╝');
        console.log('');
        console.log(`  TX ID:     ${tx.txid}`);
        console.log(`  Network:   chipnet`);
        console.log(`  Contract:  ${artifact.contractName}`);
        console.log(`  OP_RETURN: "CashScript Copilot | BCH-1 Hackcelerator 2026"`);
        console.log('');
        console.log('  Explorers:');
        console.log(`  - https://chipnet.bch.ninja/tx/${tx.txid}`);
        console.log(`  - https://cbch.loping.net/tx/${tx.txid}`);
        console.log('');

        // Save proof
        const proof = {
            tool: 'CashScript Copilot',
            hackathon: 'BCH-1 Hackcelerator 2026',
            track: 'Technology (Developer Tooling)',
            network: 'chipnet',
            contract: artifact.contractName,
            contractAddress: contract.address,
            txid: tx.txid,
            opReturn: 'CashScript Copilot | BCH-1 Hackcelerator 2026 | github.com/mthdroid/cashscript-copilot',
            explorers: [
                `https://chipnet.bch.ninja/tx/${tx.txid}`,
                `https://cbch.loping.net/tx/${tx.txid}`
            ],
            timestamp: new Date().toISOString()
        };

        writeFileSync(join(__dirname, 'proof.json'), JSON.stringify(proof, null, 2));
        console.log('  Proof saved -> proof.json');
        console.log('  Use the TX ID above in your DoraHacks submission!');
        console.log('');

    } catch (e) {
        console.error(`\n  X Transaction failed: ${e.message}`);
        console.error('  Possible causes:');
        console.error('  - Insufficient balance (need > 10000 satoshis)');
        console.error('  - Network issue (try again in a few seconds)');
        console.error('  - UTXO not yet confirmed (wait 1-2 minutes)');
        process.exit(1);
    }
}

main().catch(e => {
    console.error('\nFatal error:', e.message);
    process.exit(1);
});
