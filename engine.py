"""Simulate capability-aware scheduling of dependent agent tasks."""
import json

def analyze(data):
    tasks = {t['id']:t for t in data.get('tasks',[])}
    workers = {w['id']:w for w in data.get('workers',[])}
    if len(tasks) != len(data.get('tasks',[])) or len(workers) != len(data.get('workers',[])):
        raise ValueError('Duplicate ids')
    for task in tasks.values():
        if task['duration'] < 0: raise ValueError('Negative duration')
        if any(d not in tasks for d in task.get('depends',[])): raise ValueError('Unknown dependency')
    pending, done, available, schedule = set(tasks), {}, {w:0 for w in workers}, []
    while pending:
        ready = sorted(t for t in pending if all(d in done for d in tasks[t].get('depends',[])))
        if not ready: raise ValueError('Dependency cycle')
        candidates = []
        for tid in ready:
            task = tasks[tid]
            for wid,worker in workers.items():
                if set(task.get('requires',[])) <= set(worker.get('skills',[])):
                    start = max([available[wid]]+[done[d] for d in task.get('depends',[])])
                    candidates.append((start+task['duration'],start,tid,wid))
        if not candidates: raise ValueError('No capable worker')
        end,start,tid,wid = min(candidates)
        done[tid], available[wid] = end,end
        pending.remove(tid)
        schedule.append({'task':tid,'worker':wid,'start':start,'end':end})
    return {'schedule':schedule,'makespan':max(done.values(),default=0)}

if __name__ == '__main__':
    import argparse, sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='Path to a JSON scenario')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as source:
            data = json.load(source)
        if not isinstance(data, dict):
            raise ValueError('Input must be a JSON object')
        print(json.dumps(analyze(data), indent=2, sort_keys=True))
    except (ValueError, TypeError, KeyError, OSError) as error:
        print('Input error: '+str(error), file=sys.stderr)
        sys.exit(2)
