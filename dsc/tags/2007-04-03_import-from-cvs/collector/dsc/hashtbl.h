
typedef struct _hashitem {
	const void *key;
	void *data;
	struct _hashitem *next;
} hashitem;

typedef unsigned int hashfunc(const void *key);
typedef int hashkeycmp(const void *a, const void *b);

typedef struct {
	unsigned int modulus;
	hashitem **items;
	hashfunc *hasher;
	hashkeycmp *keycmp;
	struct {
		hashitem *next;
		unsigned int slot;
	} iter;
} hashtbl;


hashtbl *hash_create(int N, hashfunc *, hashkeycmp *);
int hash_add(const void *key, void *data, hashtbl *);
void *hash_find(const void *key, hashtbl *);
void hash_iter_init(hashtbl *);
void *hash_iterate(hashtbl *);

extern unsigned int SuperFastHash (const char * data, int len);
