"""Basic test to verify crew implementation works.

This is a minimal test that creates a simple crew and executes it
to ensure the core functionality is working.
"""

from deepagents.crew import Agent, Task, Crew, ProcessType


def test_basic_crew():
    """Test basic crew functionality."""
    print("\n" + "="*60)
    print("Testing Basic Crew Functionality")
    print("="*60 + "\n")

    # Create a simple agent
    agent = Agent(
        role="Assistant",
        goal="Help with tasks",
        backstory="You are a helpful assistant.",
        verbose=True,
    )

    # Create a simple task
    task = Task(
        description="Say hello and introduce yourself",
        expected_output="A friendly greeting and introduction",
        agent=agent,
    )

    # Create crew
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=ProcessType.SEQUENTIAL,
        verbose=True,
    )

    # Execute
    try:
        result = crew.launch()

        print("\n" + "="*60)
        print("✅ TEST PASSED")
        print("="*60)
        print(f"Result: {result.raw[:200]}")
        print(f"Execution time: {result.execution_time:.2f}s")
        print(f"Tasks completed: {len(result.tasks_output)}")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED")
        print("="*60)
        print(f"Error: {e}")
        print("="*60 + "\n")

        import traceback
        traceback.print_exc()

        return False


def test_task_context():
    """Test task dependencies via context."""
    print("\n" + "="*60)
    print("Testing Task Context (Dependencies)")
    print("="*60 + "\n")

    agent = Agent(
        role="Assistant",
        goal="Complete tasks in sequence",
        backstory="You are a helpful assistant who follows instructions.",
        verbose=True,
    )

    task1 = Task(
        description="Count from 1 to 3",
        expected_output="Three numbers: 1, 2, 3",
        agent=agent,
    )

    task2 = Task(
        description="Now count from 4 to 6, continuing from the previous count",
        expected_output="Three more numbers: 4, 5, 6",
        agent=agent,
        context=[task1],  # Depends on task1
    )

    crew = Crew(
        agents=[agent],
        tasks=[task1, task2],
        process=ProcessType.SEQUENTIAL,
        verbose=True,
    )

    try:
        result = crew.launch()

        print("\n" + "="*60)
        print("✅ TEST PASSED")
        print("="*60)
        print(f"Task 1 output: {task1.output.raw[:100]}")
        print(f"Task 2 output: {task2.output.raw[:100]}")
        print(f"Tasks completed: {len(result.tasks_output)}")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED")
        print("="*60)
        print(f"Error: {e}")
        print("="*60 + "\n")

        import traceback
        traceback.print_exc()

        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" "*20 + "CREW MODULE TESTS")
    print("="*70 + "\n")

    results = []

    # Run tests
    results.append(("Basic Crew", test_basic_crew()))
    results.append(("Task Context", test_task_context()))

    # Summary
    print("\n" + "="*70)
    print(" "*25 + "TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:30} {status}")

    print("="*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70 + "\n")

    if passed == total:
        print("🎉 All tests passed!\n")
        return 0
    else:
        print("⚠️  Some tests failed.\n")
        return 1


if __name__ == "__main__":
    exit(main())
