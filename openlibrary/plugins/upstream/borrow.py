"""Handlers for borrowing books"""

import datetime
import string

import web

from infogami import config
from infogami.utils import delegate
from infogami.utils.view import public

import utils
from utils import render_template

# Handler for /books/{bookid}/{title}/borrow
class borrow(delegate.page):
	path = "(/books/OL\d+M)/borrow"
	
	def GET(self, key):
		book = web.ctx.site.get(key)
		
		if not book:
			raise web.notfound()
			
		return render_template("borrow", book)
		
class do_borrow(delegate.page):
    """Actually borrow the book, via POST"""
    path = "(/books/OL\d+M)/_doborrow"
    
    def POST(self, key):
        i = web.input()
        
        user = web.ctx.site.get_user()
        
        everythingChecksOut = True # XXX
        if everythingChecksOut:
            # XXX get loan URL and loan id            
            resourceType = 'epub'
            loan = Loan(user.key, key, resourceType)
            loan.add()
            acs4link = loan.create_url()
            raise web.seeother(acs4link)
        else:
            # Send to the borrow page
            raise web.seeother(key + '/borrow') # XXX doesn't work because title is after OL id
            

class Loan:

    defaultLoanDelta = datetime.timedelta(weeks = 2)
    isoFormat = "%Y-%m-%dT%H:%M:%S.%f"

    def __init__(self, userKey, bookKey, resourceType, expiry = None, loanedAt = None):
        self.userKey = userKey
        self.bookKey = bookKey
        self.resourceType = resourceType
        self.type = '/type/loan'
        
        if loanedAt is not None:
            self.loanedAt = loanedAt
        else:
            self.loanedAt = datetime.datetime.utcnow().isoformat()

        if expiry is not None:
            self.expiry = expiry
        else:
            print(self.loanedAt)
            self.expiry = datetime.datetime.strptime(self.loanedAt, Loan.isoFormat)
        
    def get_key(self):
        return '%s-%s-%s' % (self.userKey, self.bookKey, self.resourceType)
        
    def get_dict(self):
        return { 'user': self.userKey, 'type': '/type/loan',
                 'book': self.bookKey, 'expiry': self.expiry,
                 'loanedAt': self.loanedAt, 'resourceType': self.resourceType }
                 
    def set_dict(self, loanDict):
        self.userKey = loanDict['user']
        self.type = loanDict['type']
        self.bookKey = loanDict['book']
        self.resourceType = loanDict['resourceType']
        self.expiry = loanDict['expiry']
        self.loanedAt = loanDict['loanedAt']
        
    def load(self):
        self.set_dict(web.ctx.site.store[self.get_key()])
        
    def save(self):
        web.ctx.site.store[self.get_key()] = self.get_dict()
        
    def add(self):
        """Record/update the loan"""
        self.save()
        
    def remove(self):
        web.ctx.site.delete(self.get_key())
        
    def create_url(self):
        """Mints a loan URL"""
        # XXX implement
        pieces = ['%s=%s' % (key, value) for (key, value) in self.get_dict().items()]
        return "/?%s" % string.join(pieces, '&')
        
             
def get_loans(user):
    return [web.ctx.site.store[result['key']] for result in web.ctx.site.store.query('/type/loan', 'user', user.key)]
    