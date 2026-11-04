from pawpal_system import Pet, Owner, Scheduler, Task

owner = Owner("Julia")
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
owner.add_pet(zack)
owner.add_pet(smudge)

# Create empty schedule
schedule = Scheduler(owner)

plan = schedule.generate_plan()

print(f"Today's schedule for {owner.name}:")
for task in plan:
    time = task.time or "Anytime"
    print(f"  {time:<8} {task.description:<22} {task.pet_name:<8} "
          f"{task.duration_minutes:>3} min  [{task.priority}]")
