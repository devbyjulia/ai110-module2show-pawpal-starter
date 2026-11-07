from pawpal_system import Pet, Owner, Scheduler, Task

owner_1 = Owner("Julia")
smudge = Pet("Smudge", "cat")
zack = Pet("Zack", "dog")

# Add at least three tasks with different times to the pets
walk_zack = Task("Take Zack for a walk", 5, "08:30", "high")
feed_zack = Task("Feed Zack", 3, "08:45", "high")
feed_smudge = Task("Feed Smudge", 3, "09:00", "high")
play_with_smudge = Task("Play with Smudge", 10, "09:30", "medium")

# Add the tasks for each pet
smudge.add_task(feed_smudge)
smudge.add_task(play_with_smudge)

zack.add_task(feed_zack)
zack.add_task(walk_zack)

# Add the pets to owner list
owner_1.add_pet(zack)
owner_1.add_pet(smudge)

# Create empty schedule
schedule_1 = Scheduler(owner_1)

plan_1 = schedule_1.generate_plan()

print(f"Today's schedule for {owner_1.name}:")
for task in plan_1:
    time = task.time or "Anytime"
    print(f"  {time:<8} {task.description:<22} {task.pet_name:<8} "
          f"{task.duration_minutes:>3} min  [{task.priority}]")

# Add tasks out of order and print the results
owner_2 = Owner("Gary")
goldie = Pet("Goldie", "goldfish")

clean_tank = Task("Clean Goldie's tank", 25, "13:30", "high")
feed_goldie = Task("Feed Goldie", 2, "08:30", "high")

goldie.add_task(clean_tank)
goldie.add_task(feed_goldie)

print("\nTasks out of order:")
for task in goldie.tasks:
    time = task.time or "Anytime"
    print(f"  {time:<8} {task.description:<22} {task.pet_name:<8} "
          f"{task.duration_minutes:>3} min  [{task.priority}]")

schedule_2 = Scheduler(owner_2)

sorted_schedule_2 = schedule_2.sort_by_time(goldie.tasks)
print(f"\nSorted tasks for {owner_2.name}:")
for task in sorted_schedule_2:
    time = task.time or "Anytime"
    print(f"  {time:<8} {task.description:<22} {task.pet_name:<8} "
          f"{task.duration_minutes:>3} min  [{task.priority}]")

# Detect task conflicts
# Add another tasks that conflicts with tank cleaning
goldie_photoshoot = Task("Photoshoot with Goldie", 25, "13:30", "high")
print("\nConflicting task:")
print(f"  {"13:30":<8} {"Photoshoot with Goldie":<22} {"Goldie":<8} "
          f"{"25":>3} min  [{"high"}]")

goldie.add_task(goldie_photoshoot)

conflicts = schedule_2.detect_conflicts(goldie.tasks)

print("\nConflict warnings: ", conflicts)