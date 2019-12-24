// javascript client for github v4 graphQL API
// list all forks of a repository
// including commit count, modify date, github stars
// public domain + zero warranty



// original repository

let repoOwner = "rugantio"
let repoName = "fbcrawl"



// basic auth
// only for testing

let username = 'your_github_username'
let password = 'your_github_password'

// TODO use OAuth2 token
// https://github.com/octokit/auth-oauth-app.js



// node.js
// npm install node-fetch

const fetch = require('node-fetch')
Headers = fetch.Headers

function btoa(s){
  return Buffer.from(s, 'binary').toString('base64')
}



let headers = new Headers({

  // TODO use oauth token
  'Authorization': 'Basic '+btoa(username+":"+password),
  
  'Content-Type': 'application/json',
  'Accept': 'application/json',
})



// graphQL query string
// inspired by
// https://gist.github.com/thewoolleyman/2294542455a8e673e0a844362e0b8bac
// https://gist.github.com/jonathansick/8bbe88a85addaeeea4e7fe9ef15b016b

// TODO clean up

let graph_query = `
query (
  $repoOwner: String!,
  $repoName: String!,
  $refOrder: RefOrder!,
  $forksPerPage: Int!, # forks per page
  $forksCursor: String, # forks pagination cursor
) {
  #repository (owner:"rugantio", name:"fbcrawl") {
  repository (
    owner: $repoOwner,
    name: $repoName,
  ) {
    nameWithOwner
    pushedAt
    #updatedAt
    stargazers {
      ## StargazerConnection
      totalCount
    }
    #commitComments(first:10) {
    #  totalCount
    #}
    #isFork
    forkCount

    refs(refPrefix: "refs/", first: 100) {
    #refs(refPrefix: "refs/heads/", first: 100) {
      ##RefConnection
      #totalCount
      ## only one head?
      #pageInfo {
      #  hasNextPage
      #}
      #edges { node {
      nodes {
        #name # = heads/master
        target {
          ... on Commit {
            history(first: 5) {
              totalCount # = total_commits of original
              #edges {
              #  node {
              #    oid
              #    messageHeadline
              #    committedDate
              #    #message
              #    #author {
              #    #  name
              #    #  email
              #    #  date
              #    }
              #  }
              #}
            }
          }
        }
      }
      #}
    }

    forks(
      first: $forksPerPage,
      after: $forksCursor,
    ) {
      totalCount
      #totalDiskUsage
      ## forks pagination
      pageInfo {
        endCursor
        hasNextPage
        hasPreviousPage
        startCursor
      }
      #nodes {
      edges{
        #cursor
        node{
          ... on Repository {
            nameWithOwner
            pushedAt
            #updatedAt
            stargazers {
              totalCount
            }

            refs(refPrefix:"refs/",orderBy:$refOrder,first:1){
              #edges{ node{
              nodes{
                ... on Ref{
                  target{
                    ... on Commit{
                      history(first:10){
                        totalCount # = total_commits of fork
                        #edges{
                        #  node{
                        #    ... on Commit{
                        #      committedDate
                        #    }
                        #  }
                        #}
                      }
                    }
                  }
                }
              }
              #}
            }
          }
        }
      }
    }
  }
}
`



// debug helper
// print object properties

function dumpVars(R, s){
  s.split('\n').forEach(L => {
    n = L.split('//')[0].trim()
    if (n == '') {
      return
    }
    n2 = n.slice(1+n.indexOf('.'))
    v = eval('R.'+n2) // R = local root object
    console.log(n+' = '+v)
  })
}



// TODO retry loop, using retry-fetch ?
/*
var fetch = require('fetch-retry');

fetch(url, {
  // retry on status 403 Forbidden
  retryOn: [403],
  // Exponential backoff
  retryDelay: function(attempt, error, response) {
    return Math.pow(2, attempt) * 1000; // 1000, 2000, 4000
  },
})
.then(function(response) {
  return response.json();
})
.then(function(json) {
  // do something with the result
  console.log(json);
});
*/



// TODO use graphQL client library
// with pagination plugin?

// https://github.com/octokit/graphql.js
// GitHub GraphQL API client for browsers and Node

// https://github.com/graphql/graphql-js
// A reference implementation of GraphQL
// for JavaScript http://graphql.org/graphql-js/



// send graphQL query, process result
// pagination via recursion

function gql_fetch(url, headers, query, vars){
  return fetch(url, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      query: graph_query,
      variables: vars,
  }),
  })
  .then(r => r.json())
  .then(r => {

    // print all the data
    console.log(JSON.stringify(r, null, '  '))

    r = r.data.repository // root node

    // original repository
    dumpVars(r, `
      r.nameWithOwner
      r.pushedAt
      r.stargazers.totalCount
      r.forkCount
      r.refs.nodes[0].target.history.totalCount // original commits
    `)

    // fork repositories
    //r.forks.nodes.forEach(f => {
    r.forks.edges.forEach(e => {
      /*
        dumpVars(e,`
        e.cursor
      `)
      */
      f = e.node
      dumpVars(f, `
        f.nameWithOwner
        f.pushedAt
        f.stargazers.totalCount
        f.refs.nodes[0].target.history.totalCount // fork commits
      `)
    })

    // forks pagination
    const {hasNextPage, endCursor} = r.forks.pageInfo

    if (hasNextPage) {
      console.log('next page ....')

      // recursion
      vars.forksCursor = endCursor
      return gql_fetch(
        url,
        headers,
        query,
        vars
      )

    }
    else {
      console.log('last page done')
    }

  })

}



// send query

gql_fetch(
  'https://api.github.com/graphql',
  headers,
  graph_query, {
  refOrder: {
    direction: "DESC",
    field: "TAG_COMMIT_DATE",
  },
  repoOwner: repoOwner,
  repoName: repoName,
  forksCursor: null, // first page
  forksPerPage: 100,
})
