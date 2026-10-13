---
title: Git(Hub), Hugo and Academic
date: '2018-02-07T18:31:37Z'
draft: false
---
> **Update:** This post describes the original Academic/Netlify-era setup that this site later migrated away from. The steps below are kept for historical reference only and may no longer match the current Hugo Blox + GitHub Actions workflow.

A quick(ish) tutorial on how I setup my personal but work related [website](https://scott-love.github.io) using Git(Hub), Hugo and Academic on a Mac. This is a fairly *simple* and completely *free* way to host an academic personal website. The process came from two main sources: 1. The [documentation](https://sourcethemes.com/academic/docs/) for Academic and; 2. A blog post by [George Cushen](https://georgecushen.com/create-your-website-with-hugo/).

## So what did I do:

* I already had [Git installed](https://git-scm.com/downloads) and you will need it too.

* Then install [Hugo](https://gohugo.io/about/). There are several options but I used the Tarball method. Full details can be found [here](https://gohugo.io/getting-started/installing/) but here is a brief description.
  1. Chose install location (e.g., /usr/local/bin), in your executable PATH.
  2. Download the latest [Tarball](https://github.com/gohugoio/hugo/releases) for your system to the Downloads folder.
  3. Install Hugo in your chosen location.
  ```
  cd /usr/local/bin # CHOSEN_INSTALL_LOCATION
  # extract the tarball
  tar -xvzf ~/Downloads/hugo_X.Y_osx-64bit.tgz
  # verify that it runs
  ./hugo version
  ```

* [Fork](https://help.github.com/articles/fork-a-repo/) the [Academic Kickstart](https://github.com/sourcethemes/academic-kickstart#fork-destination-box) repository to your GitHub account.
 1. Login to your GitHub account.
 2. Click [here](https://github.com/sourcethemes/academic-kickstart#fork-destination-box) or search for sourcethemes/academic-kickstart inside GitHub.
 3. Click on the fork icon towards the top right of the screen.
<br/><br/>
* [Clone](https://git-scm.com/docs/git-clone) the repository onto your local system. Note that you need to change \<USERNAME\> to your GitHub username and that My_Website can be changed to any name you want.
```
git clone https://github.com/<USERNAME>/academic-kickstart.git My_Website
```

* Initialise the theme.
```
cd My_Website
git submodule update --init --recursive
```

* Create your GitHub website repository.
  1. On your GitHub page click the “+” icon in the top right corner and choose “New Repository”.
  2. Repository name = \<USERNAME\>.github.io.
<br/><br/>
* Add your \<USERNAME\>.github.io repository into a submodule folder named public.
```
git submodule add https://github.com/<USERNAME>/<USERNAME>.github.io.git public
```

* [Add](https://git-scm.com/docs/git-add) to the local git repository then [push](https://git-scm.com/docs/git-push) to the remote repository.
```
git add .
git commit -m "initial commit"
git push -u origin master
```

* Run Hugo to create the HTML for the site.
```
hugo server
```

* View the built site in your browser (http://localhost:1313/) but note this is only a local copy and not visible to others.

* Upload the built site to Github for everyone to see @ \<USERNAME\>.github.io. Note it will take 2 or 3 minutes to be viewable.
```
git add .
git commit -m "build website"
git push -u origin master
```

## Adding content:
OK, the website is built it's time to add content. You can make additions/changes to your website and check out the results before deploying to your actual site.

A good place to start is the config.toml file in the main directory of your site.
It contains a bunch of key-value pairs. change the title value to the title of your website, e.g., your name. Then run Hugo server to create the HTML for the site.
```
hugo server
```
View the local copy of the built site in your browser (http://localhost:1313/).
Leave the server running and any other changes you make will be automatically visible in local site just created. Go through all the key-value pairs and change, edit or remove any that you want.

## Github version control:
The [Host on GitHub](https://gohugo.io/hosting-and-deployment/hosting-on-github/#github-user-or-organization-pages) page from Hugo outlines a nice way to store all the files of your site on GitHub.

## Updating the website content:
Using the GitHub method above I do not keep a local copy of any of the files. Here is the process I follow to update the website content.
```
git clone https://github.com/<USERNAME>/<YOUR-PROJECT>
cd <YOUR-PROJECT>/
git rm -r public
```
At this point you can make changes to the content of your website and push those to the remote repository.

```
git add .
git commit -m "updating content"
git push origin master
```

However, this only keeps the content in synchrony with the remote repository it does not update the website.

```
git submodule add https://github.com/<USERNAME>/<USERNAME>.github.io.git public
./deploy.sh "comment"
```
The contents of deploy.sh can be seen [here](https://gohugo.io/hosting-and-deployment/hosting-on-github/#github-user-or-organization-pages)

## Update academic-kickstart version:
I have found updating the academic-kickstart version and subsequently the website to be tricky! Follow the instructions [here](https://sourcethemes.com/academic/docs/update/). However, I was only ever able to update using the ZIP  there. Uninstall the current version by deleting the contents of the "themes/academic/" folder inside \<YOUR-PROJECT\> and replacing it with the downloaded files.

At this point you still need to follow the release notes and update your content and config files to take into account the "Breaking changes". If you have jumped a few versions you will need to do this in sequence for each version change (e.g. v3.1 to v3.2 before doing v3.2 to v3.3)
