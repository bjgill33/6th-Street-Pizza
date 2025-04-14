# Merging changes from the main branch to the production branch

Development should occur on the `main` branch.
When changes are to be tested on the production server, these these changes must be merged from the `main` branch, into the Production `branch`. This guide details how to merge changes from the main branch to the production branch.

Prerequisites

- Git
- VSCode (or other code editor)

This guide assumes you have the project git repository cloned and setup on your computer. See [Local Setup](./local_setup.md)

## Step 1

Open your editor to the 6th street pizza project.

Open a command line terminal in your editor. `CTRL+~` Should open one up in VSCode. Alternatively, any Command Prompt/Powershell/Terminal in the project directory should work.

## Step 2

Fetch changes from github

```shell
git fetch
```

## Step 3

In the terminal, run

```shell
git status
```

You should see an output like this:

```
On branch main
Your branch is up to date with 'origin/main'.

...
```

## Step 4

Change the current active branch to the production branch

```shell
git switch Production
```

Run

```shell
git status
```

Again to verify you have switched branches.
You should an output like this:

```
On branch Production
Your branch is up to date with 'origin/Production'.

nothing to commit, working tree clean
```

## Step 5
