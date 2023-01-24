#include <cstdlib>
#include <cstdio>
#include <cinttypes>
#include <cstring>
#include <unordered_map>
#include <unordered_set>
#include <map>
#include <set>

#define ADDRCELLSIZE 8
#define THREADCELLSIZE 4

#ifdef DBGBUF
extern "C" {
#include "vamos-buffers/shmbuf/buffer.h"
}

std::map<void *, const char *> _vars;
static vms_shm_dbg_buffer *dbgbuf;
void update_dbgbuf() {
    static size_t version = 0;
    if (!dbgbuf) {
        dbgbuf = vms_shm_dbg_buffer_get("/vrd-vars");
    }

    if (dbgbuf) {
        size_t buf_version = vms_shm_dbg_buffer_version(dbgbuf);
        if (buf_version > version) {
            version = buf_version;
            const size_t recsize = vms_shm_dbg_buffer_rec_size(dbgbuf);
            const size_t size = vms_shm_dbg_buffer_size(dbgbuf);
            unsigned char *data =  vms_shm_dbg_buffer_data(dbgbuf);
            for (size_t i = 0; i < size; ++i) {
                unsigned char *rec = data + recsize*i;
                void *addr;
                memcpy(&addr, rec, sizeof(addr));
                const char *name = (char*)(rec + sizeof(void*));
                _vars[*(void**)rec] = (char*)(rec + sizeof(void*));
            }
        }
    }
}

// returns base address and name
std::pair<void *, const char *> get_var(void *addr) {
    update_dbgbuf();

    auto it = _vars.lower_bound(addr);
    if (it == _vars.end())
        return {nullptr, nullptr};
    if (it->first != addr) {
        // it is the greater element
        if (it == _vars.begin()) {
            return {nullptr, nullptr};
        }
        // return the lower element
        --it;
    }
    return *it;
}
#else
std::pair<void *, const char *> get_var(void *addr) { return {nullptr, nullptr}; }
#endif

using namespace std;

enum class ActionType {
	ATRead, ATWrite, ATLock, ATUnlock, ATAlloc, ATFree, ATFork, ATJoin, ATSkipStart, ATSkipEnd, ATDone
};

typedef union {
	struct { intptr_t addr; } read;
	struct { intptr_t addr; } write;
	struct { intptr_t addr; } lock;
	struct { intptr_t addr; } unlock;
	struct { intptr_t addr; size_t size; } alloc;
	struct { intptr_t addr; } free;
	struct { int newthreadid; } fork;
	struct { int threadid; } join;
} Action;

void print_action(ActionType type, Action &act)
{
	switch(type)
	{
		case ActionType::ATRead:
		printf("read(%li)",act.read.addr);
		break;
		case ActionType::ATWrite:
		printf("write(%li)",act.write.addr);
		break;
		case ActionType::ATLock:
		printf("lock(%li)",act.lock.addr);
		break;
		case ActionType::ATUnlock:
		printf("unlock(%li)",act.unlock.addr);
		break;
		case ActionType::ATAlloc:
		printf("alloc(%li, %lu)",act.alloc.addr, act.alloc.size);
		break;
		case ActionType::ATFree:
		printf("free(%li)",act.free.addr);
		break;
		case ActionType::ATFork:
		printf("fork(%i)",act.fork.newthreadid);
		break;
		case ActionType::ATJoin:
		printf("join(%i)",act.join.threadid);
		break;
		case ActionType::ATSkipStart:
		printf("skipstart()");
		break;
		case ActionType::ATSkipEnd:
		printf("skipend()");
		break;
		case ActionType::ATDone:
		printf("done()");
		break;
	}
}

class Cell {
	public:
	Cell * next;
	size_t refcount;
	uint64_t timestamp;
	int threadid;
	ActionType type;
	Action action;
};

Cell * head=new Cell();
Cell * tail=head;
size_t cellcount=0;
uint64_t racecount=0;

extern "C" uint64_t GetRaceCount() { return racecount; }

class Lockset
{
	public:
	unordered_set<intptr_t> addrs;
	unordered_set<int> threads;
	unordered_set<int> skipthreads;
	unordered_set<int> skippedthreads;
};

class Info {
	public:
	Info(int owner):owner(owner),pos(0),alock(0),lockset()
	{
		pos=tail;
		lockset.threads.insert(owner);
	}
	Info(Info &a) =delete;
	Info(const Info &a) =delete;
	int owner;
	Cell * pos;
	intptr_t alock;
	Lockset lockset;
};

unordered_map<intptr_t, Info> Writes;
unordered_map<intptr_t, map<int, Info>> Reads;
unordered_map<intptr_t, int> LockThreads;
map<int, set<intptr_t>> ThreadLocks;

void print_lockset(Lockset &ls, bool printNewline=true)
{
	printf("Lockset %p = (addrs : {", (void*)&ls);
	bool seenfirst=false;
	for(auto addr : ls.addrs)
	{
		if(seenfirst)
		{
			printf(", ");
		}
		printf("%p", (void*)addr);
		seenfirst=true;
	}
	printf("}, threads: {");
	seenfirst=false;
	for(auto thrd : ls.threads)
	{
		if(seenfirst)
		{
			printf(", ");
		}
		printf("%i", thrd);
		seenfirst=true;
	}
	printf("})");
	if(printNewline)
	{
		printf("\n");
	}
}

void print_cell(Cell &cell, bool printRest=false)
{
	printf("Cell %p = (ts : %lu, thrd: %i, act: ", (void*)&cell, cell.timestamp, cell.threadid);
	print_action(cell.type, cell.action);
	printf(")");
	if(printRest&&cell.next!=0&&cell.next!=tail)
	{
		printf("; ");
		print_cell(*cell.next, true);
	}
	else
	{
		printf("\n");
	}
}

void print_info(Info &info, bool printCells=false)
{
	printf("Info %p = (owner: %i, alock: %li, ",(void*)&info, info.owner, info.alock);
	print_lockset(info.lockset,false);
	printf(")");
	if(printCells)
	{
		printf("; ");
		if(info.pos!=0&&info.pos!=tail)
		{
			print_cell(*info.pos,true);
		}
		else
		{
			printf("\n");
		}
	}
	else
	{
		printf("\n");
	}
}

void cell_rc_inc(Cell* cell)
{
	cell->refcount++;
}
void cell_rc_dec(Cell* cell)
{
	cell->refcount--;
	if(cell->refcount<=0)
	{
		if(cellcount>10000&&head->refcount==0)
		{
			while(head->refcount==0&&head->next!=0)
			{
				Cell* last=head;
				head=head->next;
				cellcount--;
				free(last);
			}
		}
	}
}

inline void enqueue_sync_event(int thrd, ActionType tp, Action &a)
{
	tail->threadid=thrd;
	tail->action=a;
	tail->type=tp;
	tail->next=new Cell();
	tail=tail->next;
	cellcount++;
}

inline bool thread_holds_lock(int thrd, intptr_t lock)
{
	auto posn = LockThreads.find(lock);
	if(posn!=LockThreads.end())
	{
		return (*posn).second==thrd;
	}
	return false;
}

void apply_lockset_rules(Lockset &ls, Cell **pos1r, Cell *pos2, int owner2, ActionType action, intptr_t addr, int otherthread)
{
	Cell* pos1=*pos1r;
	Cell* origpos1=pos1;
	while(pos1!=pos2)
	{
		switch(pos1->type)
		{
			case ActionType::ATLock:
			{
				if(ls.addrs.find(pos1->action.lock.addr)!=ls.addrs.end()||!ls.skipthreads.empty()||!ls.skippedthreads.empty())
				{
					ls.threads.insert(pos1->threadid);
				}
			}
			break;
			case ActionType::ATUnlock:
			{
				if(ls.threads.find(pos1->threadid)!=ls.threads.end()||ls.skipthreads.find(pos1->threadid)!=ls.skipthreads.end()||ls.skippedthreads.find(pos1->threadid)!=ls.skippedthreads.end())
				{
					ls.addrs.insert(pos1->action.unlock.addr);
				}
			}
			break;
			case ActionType::ATAlloc:
			{

			}
			break;
			case ActionType::ATFree:
			{

			}
			break;
			case ActionType::ATFork:
			{
				if(ls.threads.find(pos1->threadid)!=ls.threads.end()||ls.skipthreads.find(pos1->threadid)!=ls.skipthreads.end()||ls.skippedthreads.find(pos1->threadid)!=ls.skippedthreads.end())
				{
					ls.threads.insert(pos1->action.fork.newthreadid);
				}
			}
			break;
			case ActionType::ATJoin:
			{
				if(ls.threads.find(pos1->action.join.threadid)!=ls.threads.end()||ls.skipthreads.find(pos1->action.join.threadid)!=ls.skipthreads.end()||ls.skippedthreads.find(pos1->action.join.threadid)!=ls.skippedthreads.end())
				{
					ls.threads.insert(pos1->threadid);
				}
			}
			break;
			case ActionType::ATDone:
			{
			}
			break;
			// case ActionType::ATRead:
			// {
			// 	if((!ls.addrs.empty())&&ls.addrs.find(pos1->action.read.addr)==ls.addrs.end()&&ls.skipthreads.find(pos1->threadid)==ls.skipthreads.end()&&ls.skippedthreads.find(pos1->threadid)==ls.skippedthreads.end())
			// 	{
			// 		printf("Found data race: Thread %i read from %li without synchronization\n", pos1->threadid, pos1->action.read.addr);
			// 	}
			// 	else
			// 	{
			// 		printf("read is fine\n");
			// 	}
			// 	ls.addrs.clear();
			// 	if(ls.threads.size()!=1||(*ls.threads.begin())!=pos1->threadid)
			// 	{
			// 		ls.threads.clear();
			// 		ls.threads.insert(pos1->threadid);
			// 	}
			// 	ls.skippedthreads.clear();
			// }
			// break;
			// case ActionType::ATWrite:
			// {
			// 	if((!ls.addrs.empty())&&ls.addrs.find(pos1->action.write.addr)==ls.addrs.end()&&ls.skipthreads.find(pos1->threadid)==ls.skipthreads.end()&&ls.skippedthreads.find(pos1->threadid)==ls.skippedthreads.end())
			// 	{
			// 		fprintf(stderr, "Found data race: Thread %i wrote to %li without synchronization\n", pos1->threadid, pos1->action.write.addr);
			// 	}
			// 	else
			// 	{
			// 		printf("write is fine\n");
			// 	}
			// 	ls.addrs.clear();
			// 	if(ls.threads.size()!=1||(*ls.threads.begin())!=pos1->threadid)
			// 	{
			// 		ls.threads.clear();
			// 		ls.threads.insert(pos1->threadid);
			// 	}
			// 	ls.skippedthreads.clear();
			// }
			// break;
			case ActionType::ATSkipStart:
			{
				ls.skipthreads.insert(pos1->threadid);
			}
			break;
			case ActionType::ATSkipEnd:
			{
				ls.skipthreads.erase(pos1->threadid);
				ls.skippedthreads.insert(pos1->threadid);
			}
			break;
		}
		pos1=pos1->next;
		*pos1r=pos1;
	}
	cell_rc_inc(pos1);
	cell_rc_dec(origpos1);
	switch(action)
	{		
		case ActionType::ATRead:
		{
			if((!(ls.addrs.empty()&&ls.threads.empty()))&&ls.threads.find(owner2)==ls.threads.end()&&ls.skipthreads.find(owner2)==ls.skipthreads.end()&&ls.skippedthreads.find(owner2)==ls.skippedthreads.end())
			{
#if DEBUGPRINT
				fprintf(stderr, "//Found data race: Thread %i read from %p without synchronizing with thread %i\n", owner2, (void*)addr, otherthread);
#else
#ifdef DBGBUF
                auto [base, var] = get_var((void*)addr);
                if (var) {
                    if (base != (void*)addr) {
				        fprintf(stderr, "Found data race: Thread %i read from '%s+%lu'[%p] without synchronizing with thread %i\n",
                                owner2, var, addr - (intptr_t)base, (void*)addr, otherthread);

                    } else {
				        fprintf(stderr, "Found data race: Thread %i read from '%s'[%p] without synchronizing with thread %i\n",
                                owner2, var, (void*)addr, otherthread);
                    }
                } else
#endif // DBGBUF
				    fprintf(stderr, "Found data race: Thread %i read from [%p] without synchronizing with thread %i\n", owner2, (void*)addr, otherthread);
#endif
				racecount++;
			}
			// else
			// {
			// 	printf("read is fine\n");
			// }
			// ls.addrs.clear();
			// if(ls.threads.size()!=1||(*ls.threads.begin())!=owner2)
			// {
			// 	ls.threads.clear();
			// 	ls.threads.insert(owner2);
			// }
			// ls.skippedthreads.clear();
		}
		break;
		case ActionType::ATWrite:
		{
			if((!(ls.addrs.empty()&&ls.threads.empty()))&&ls.threads.find(owner2)==ls.threads.end()&&ls.skipthreads.find(owner2)==ls.skipthreads.end()&&ls.skippedthreads.find(owner2)==ls.skippedthreads.end())
			{
#if DEBUGPRINT
				fprintf(stderr, "//Found data race: Thread %i wrote to %p without synchronizing with thread %i\n", owner2, (void*)addr, otherthread);
#else
#ifdef DBGBUF
                auto [base, var] = get_var((void*)addr);
                if (var) {
                    if (base != (void*)addr) {
				        fprintf(stderr, "Found data race: Thread %i wrote to '%s+%lu'[%p] without synchronizing with thread %i\n",
                                owner2, var, addr - (intptr_t)base, (void*)addr, otherthread);

                    } else {
				        fprintf(stderr, "Found data race: Thread %i wrote to '%s'[%p] without synchronizing with thread %i\n",
                                owner2, var, (void*)addr, otherthread);
                    }

                } else
#endif //DBGBUF
				    fprintf(stderr, "Found data race: Thread %i wrote to [%p] without synchronizing with thread %i\n", owner2, (void*)addr, otherthread);
#endif
				racecount++;
			}
			// else
			// {
			// 	printf("write is fine\n");
			// }
			// ls.addrs.clear();
			// if(ls.threads.size()!=1||(*ls.threads.begin())!=owner2)
			// {
			// 	ls.threads.clear();
			// 	ls.threads.insert(owner2);
			// }
			// ls.skippedthreads.clear();
		}
		break;
	}
}

void check_happens_before(Info &info1, Info &info2, ActionType action, intptr_t addr)
{
	// print_info(info1, true);
	// print_info(info2, true);
	// if(info1->xact&&info2->xact)
	// {
	// 	return;
	// }
	if((info1.owner!=info2.owner)&&(!thread_holds_lock(info2.owner,info1.alock)))
	{
		apply_lockset_rules(info1.lockset, &info1.pos, info2.pos, info2.owner, action, addr, info1.owner);
		info2.alock=0;
		auto posn=ThreadLocks.find(info1.owner);
		if(posn!=ThreadLocks.end())
		{
			auto posn2=posn->second.begin();
			if(posn2!=posn->second.end())
			{
				info2.alock=*posn2;
			}
		}
	}
}

inline void monitor_handle_read_(int tid, uint64_t timestamp, intptr_t addr)
{
	auto &addrmap = Reads[addr];
	auto entry = addrmap.find(tid);
	cell_rc_inc(tail);
	if(entry==addrmap.end())
	{
		entry=addrmap.insert_or_assign(tid,tid).first;
	}
	else
	{
		entry->second.alock=0;
		entry->second.owner=tid;
		entry->second.lockset.addrs.clear();
		entry->second.lockset.threads.clear();
		entry->second.lockset.threads.insert(tid);
		cell_rc_dec(entry->second.pos);
		entry->second.pos=tail;
	}
	auto wentry=Writes.find(addr);
	if(wentry!=Writes.end())
	{
		check_happens_before(wentry->second,entry->second, ActionType::ATRead, addr);
	}
}

extern "C" void monitor_handle_read(int tid, uint64_t timestamp, intptr_t addr)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_read(tid=%i, ts=%lu, %p);\n", tid, timestamp, (void*)addr);
	#endif
	monitor_handle_read_(tid, timestamp, addr);
}

extern "C" void monitor_handle_read_many(int tid, uint64_t timestamp, intptr_t addr, size_t bytes)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_read_many(tid=%i, ts=%lu, %p, %lu);\n", tid, timestamp, (void*)addr, bytes);
	#endif
	for(size_t i=0;i<bytes;i++)
	{
		monitor_handle_read_(tid,timestamp,addr+i);
	}
}

inline void monitor_handle_write_(int tid, uint64_t timestamp, intptr_t addr)
{
	// printf("MWRITE! %p\n", addr);
	Info info(tid);
	cell_rc_inc(tail);
	// print_cell(*head,true);
	auto rinfo = Reads.find(addr);
	if(rinfo!=Reads.end())
	{
		for(auto &trinfo : rinfo->second)
		{
			check_happens_before(trinfo.second, info, ActionType::ATWrite, addr);
		}
	}
	// else
	// {
	// 	printf("MWRITE: no reads found, %p\n", addr);
	// }
	auto winfo = Writes.find(addr);
	if(winfo!=Writes.end())
	{
		check_happens_before(winfo->second, info, ActionType::ATWrite, addr);
		cell_rc_dec(winfo->second.pos);
		winfo->second=std::move(info);
	}
	else
	{
		Writes.insert_or_assign(addr, tid);
		// printf("MWRITE: no writes found, %p\n", addr);
	}
	if(rinfo!=Reads.end())
	{
		for(auto tlp=rinfo->second.begin();tlp!=rinfo->second.end();tlp++)
		{
			cell_rc_dec(tlp->second.pos);
		}
		rinfo->second.clear();
	}
	Reads.extract(addr);
}

extern "C" void monitor_handle_write(int tid, uint64_t timestamp, intptr_t addr)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_write(tid=%i, ts=%lu, %p);\n", tid, timestamp, (void*)addr);
	#endif
	monitor_handle_write_(tid,timestamp,addr);
}

extern "C" void monitor_handle_write_many(int tid, uint64_t timestamp, intptr_t addr, size_t bytes)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_write_many(tid=%i, ts=%lu, %p, %lu);\n", tid, timestamp, (void*)addr, bytes);
	#endif
	for(size_t i=0;i<bytes;i++)
	{
		monitor_handle_write_(tid,timestamp,addr+i);
	}
}

extern "C" void monitor_handle_lock(int tid, uint64_t timestamp, intptr_t addr)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_lock(tid=%i, ts=%lu, %p);\n", tid, timestamp, (void*)addr);
	#endif
	Action a;
	a.lock.addr=addr;
	LockThreads[addr]=tid;
	ThreadLocks[tid].insert(addr);
	enqueue_sync_event(tid, ActionType::ATLock, a);
}

extern "C" void monitor_handle_unlock(int tid, uint64_t timestamp, intptr_t addr)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_unlock(tid=%i, ts=%lu, %p);\n", tid, timestamp, (void*)addr);
	#endif
	Action a;
	a.unlock.addr=addr;
	LockThreads.erase(addr);
	ThreadLocks[tid].erase(addr);
	enqueue_sync_event(tid, ActionType::ATUnlock, a);
}

extern "C" void monitor_handle_skip_start(int tid, uint64_t timestamp)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_skip_start(tid=%i, ts=%lu);\n", tid, timestamp);
	#endif
	Action a;
	enqueue_sync_event(tid, ActionType::ATSkipStart, a);
}
extern "C" void monitor_handle_skip_end(int tid, uint64_t timestamp)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_skip_end(tid=%i, ts=%lu);\n", tid, timestamp);
	#endif
	Action a;
	enqueue_sync_event(tid, ActionType::ATSkipEnd, a);
}
extern "C" void monitor_handle_alloc(int tid, uint64_t timestamp, intptr_t addr, size_t size)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_alloc(tid=%i, ts=%lu, %p, %lu);\n", tid, timestamp, (void*)addr, size);
	#endif
	Action a;
	a.alloc.addr=addr;
	a.alloc.size=size;
	enqueue_sync_event(tid, ActionType::ATAlloc, a);
}

extern "C" void monitor_handle_free(int tid, uint64_t timestamp, intptr_t addr)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_free(tid=%i, ts=%lu, %p);\n", tid, timestamp, (void*)addr);
	#endif
	Action a;
	a.free.addr=addr;
	enqueue_sync_event(tid, ActionType::ATFree, a);
}
extern "C" void monitor_handle_fork(int tid, uint64_t timestamp, int otherthread)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_fork(tid=%i, ts=%lu, %i);\n", tid, timestamp, otherthread);
	#endif
	Action a;
	a.fork.newthreadid=otherthread;
	enqueue_sync_event(tid, ActionType::ATFork, a);
}

extern "C" void monitor_handle_join(int tid, uint64_t timestamp, int otherthread)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_join(tid=%i, ts=%lu, %i);\n", tid, timestamp, otherthread);
	#endif
	Action a;
	a.join.threadid=otherthread;
	enqueue_sync_event(tid, ActionType::ATJoin, a);
}

extern "C" void monitor_handle_done(int tid, uint64_t timestamp)
{
	#ifdef DEBUGPRINT
	printf("monitor_handle_done(tid=%i, ts=%lu);\n", tid, timestamp);
	#endif
	Action a;
	enqueue_sync_event(tid, ActionType::ATDone, a);
	ThreadLocks.erase(tid);
	bool eraseNext=false;
	intptr_t eraseKey=0;
	for(auto &entry : LockThreads)
	{
		if(eraseNext)
		{
			LockThreads.erase(eraseKey);
			eraseNext=false;
		}
		if(entry.second==tid)
		{
			eraseKey=entry.first;
			eraseNext=true;
			break;
		}
	}
	if(eraseNext)
	{
		LockThreads.erase(eraseKey);
	}
}
