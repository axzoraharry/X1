"""
Blockchain API Routes - Happy Paisa Blockchain Operations
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from ..services.blockchain_gateway_service import blockchain_gateway, TransactionType, TransactionStatus
from ..models.user import User

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])

@router.get("/status")
async def get_blockchain_status():
    """Get blockchain network status"""
    try:
        status = await blockchain_gateway.get_chain_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get blockchain status: {str(e)}")

@router.get("/network/stats")
async def get_network_stats():
    """Get network statistics"""
    try:
        stats = await blockchain_gateway.get_network_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get network stats: {str(e)}")

@router.get("/user/{user_id}/address")
async def get_user_address(user_id: str):
    """Get or create blockchain address for user"""
    try:
        address = await blockchain_gateway.get_or_create_user_address(user_id)
        return address.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user address: {str(e)}")

@router.get("/user/{user_id}/balance")
async def get_user_blockchain_balance(user_id: str):
    """Get user's Happy Paisa balance on blockchain"""
    try:
        balance = await blockchain_gateway.get_user_balance(user_id)
        return balance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user balance: {str(e)}")

@router.post("/user/{user_id}/mint")
async def mint_happy_paisa(
    user_id: str,
    amount_hp: float = Query(..., description="Amount of Happy Paisa to mint"),
    reference_id: Optional[str] = Query(None, description="Reference ID for the mint operation")
):
    """Mint Happy Paisa tokens for user (INR -> HP conversion)"""
    try:
        if amount_hp <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        if amount_hp > 10000:  # Safety limit
            raise HTTPException(status_code=400, detail="Amount exceeds maximum mint limit")
        
        tx_hash = await blockchain_gateway.mint_happy_paisa(user_id, amount_hp, reference_id)
        
        return {
            "success": True,
            "message": f"Minted {amount_hp} HP for user {user_id}",
            "transaction_hash": tx_hash,
            "amount_hp": amount_hp,
            "amount_inr": amount_hp * 1000,
            "network": "happy-paisa-mainnet"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mint Happy Paisa: {str(e)}")

@router.post("/user/{user_id}/burn")
async def burn_happy_paisa(
    user_id: str,
    amount_hp: float = Query(..., description="Amount of Happy Paisa to burn"),
    reference_id: Optional[str] = Query(None, description="Reference ID for the burn operation")
):
    """Burn Happy Paisa tokens for user (HP -> INR conversion)"""
    try:
        if amount_hp <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        
        tx_hash = await blockchain_gateway.burn_happy_paisa(user_id, amount_hp, reference_id)
        
        return {
            "success": True,
            "message": f"Burned {amount_hp} HP for user {user_id}",
            "transaction_hash": tx_hash,
            "amount_hp": amount_hp,
            "amount_inr": amount_hp * 1000,
            "network": "happy-paisa-mainnet"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to burn Happy Paisa: {str(e)}")

@router.post("/transfer")
async def transfer_happy_paisa(
    from_user_id: str = Query(..., description="Sender user ID"),
    to_user_id: str = Query(..., description="Recipient user ID"),
    amount_hp: float = Query(..., description="Amount of Happy Paisa to transfer"),
    description: Optional[str] = Query(None, description="Transfer description")
):
    """Transfer Happy Paisa between users on blockchain"""
    try:
        if amount_hp <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        if from_user_id == to_user_id:
            raise HTTPException(status_code=400, detail="Cannot transfer to same user")
        
        tx_hash = await blockchain_gateway.transfer_happy_paisa(
            from_user_id, to_user_id, amount_hp, description
        )
        
        return {
            "success": True,
            "message": f"Transferred {amount_hp} HP from {from_user_id} to {to_user_id}",
            "transaction_hash": tx_hash,
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "amount_hp": amount_hp,
            "network": "happy-paisa-mainnet"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer Happy Paisa: {str(e)}")

@router.get("/transaction/{tx_hash}")
async def get_transaction_status(tx_hash: str):
    """Get blockchain transaction status"""
    try:
        transaction = await blockchain_gateway.get_transaction_status(tx_hash)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transaction status: {str(e)}")

@router.get("/user/{user_id}/transactions")
async def get_user_transactions(
    user_id: str,
    limit: int = Query(default=50, le=100, description="Maximum number of transactions to return")
):
    """Get user's blockchain transaction history"""
    try:
        transactions = await blockchain_gateway.get_user_transactions(user_id, limit)
        return {
            "user_id": user_id,
            "transactions": transactions,
            "count": len(transactions),
            "network": "happy-paisa-mainnet"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user transactions: {str(e)}")

@router.post("/sync/transaction/{tx_hash}")
async def sync_transaction_status(tx_hash: str):
    """Sync transaction status from blockchain to database"""
    try:
        await blockchain_gateway.sync_transaction_status(tx_hash)
        return {
            "success": True,
            "message": f"Synced transaction {tx_hash}",
            "transaction_hash": tx_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync transaction: {str(e)}")

@router.get("/explorer/latest-blocks")
async def get_latest_blocks(limit: int = Query(default=10, le=50)):
    """Get latest blocks information (simplified for demo)"""
    try:
        chain_info = await blockchain_gateway.get_chain_status()
        current_block = chain_info["chain_info"]["currentBlock"]
        
        # Generate mock block data
        blocks = []
        for i in range(limit):
            block_number = current_block - i
            blocks.append({
                "block_number": block_number,
                "block_hash": f"0x{block_number:064x}",
                "timestamp": datetime.utcnow().isoformat(),
                "transactions_count": 3 + (block_number % 10),
                "validator": "5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty"
            })
        
        return {
            "latest_blocks": blocks,
            "network": "happy-paisa-mainnet"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get latest blocks: {str(e)}")

@router.get("/explorer/search/{query}")
async def blockchain_search(query: str):
    """Search for transactions, blocks, or addresses"""
    try:
        results = {
            "query": query,
            "results": []
        }
        
        # Check if it's a transaction hash
        if query.startswith("0x") and len(query) == 66:
            try:
                transaction = await blockchain_gateway.get_transaction_status(query)
                results["results"].append({
                    "type": "transaction",
                    "data": transaction
                })
            except:
                pass
        
        # Check if it's an address
        elif query.startswith("5") and len(query) == 48:
            try:
                balance_info = await blockchain_gateway.chain.get_balance(query)
                results["results"].append({
                    "type": "address",
                    "data": {
                        "address": query,
                        "balance_hp": balance_info["balance_hp"],
                        "balance_inr_equiv": balance_info["balance_inr_equiv"]
                    }
                })
            except:
                pass
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/health")
async def blockchain_health():
    """Blockchain service health check"""
    try:
        status = await blockchain_gateway.get_chain_status()
        return {
            "status": "healthy",
            "service": "blockchain_gateway",
            "chain_status": status["status"],
            "network": "happy-paisa-mainnet",
            "features": {
                "minting": "operational",
                "burning": "operational",
                "transfers": "operational",
                "balance_queries": "operational"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "blockchain_gateway",
            "error": str(e)
        }