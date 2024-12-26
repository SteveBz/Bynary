#!/usr/bin/env python

# mport fdb
import inspect
import time

def escape(value):
    value = value.strip()
    value = value.replace("'", "\\'")
    
class sql:
    # Base SQL statement from which others are derived
    def __init__(self, connect, table):
        self.sort = {}
        self.attribute = {}
        #self.having = {}
        #self.groupBy = {}
        self.where = {}
        self.whereOp = {}
        #self.whereOr = {}
        self.table = table.strip()
        self.connect = connect
        
    def setTable(self, table):
        self.table = table.strip()
    def setConnect(self, connect):
        self.connect=connect
        
        
    def setWhereOrList(self, key, valueClause):
        # Must include = sign, or other comparative, Null, quotes etc.
        self.where[key] = valueClause
        self.whereOp[key] = 'OR'
    
        
    def setWhereInList(self, key, valueClause):
        # Must include = sign, or other comparative, Null, quotes etc.
        self.where[key] = valueClause
        self.whereOp[key] = 'IN'
        
    def setWhereAndList(self, key, valueClause):
        # Must include = sign, or other comparative, Null, quotes etc.
        self.where[key] = valueClause
        self.whereOp[key] = 'AND'
    
    def setWhereValueString(self, key, value):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.where[key] = "'"+str(value.strip())+ "'"
    
    def setWhereValueBool(self, key, value):
        # convert to Bool if int.
        self.where[key] = bool(value)
    
    def setWhereValueNEString(self, key, value):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.where[key] = "'"+str(value.strip())+ "'"
        self.whereOp[key] = "<>"
        
    def setWhereValueDateTime(self, key, datetime):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        key="CAST("+key+" AS TIMESTAMP)"
        #print date
        value = "cast ('"+datetime+"' as TIMESTAMP)"
        self.where[key] = value
    def setWhereValueDate(self, key, date):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        key="CAST("+key+" AS DATE)"
        #print date
        value = "cast ('"+date+"' as date)"
        self.where[key] = value
        
    def setWhereValueEQFloat(self, key, value):
        # Convert to integer
        try:
            self.where[key] = float(value)
        except Exception:
            self.where[key] = None
            
    def setWhereValueEQNull(self, key):
        # Set to null (it will be converted later)
        self.where[key] = None


    #def setWhereOr(self, key):
    #    # Convert to integer
    #    self.whereOr[key] = True

    def setWhereValueLEFloat(self, key, value):
        # Convert to integer
        try:
            self.where[key] = float(value)
            self.whereOp[key] = "<="
        except Exception:
            self.where[key] = None

    def setWhereValueLTFloat(self, key, value):
        # Convert to integer
        #print (key)
        #print(value)
        try:
            self.where[key] = float(value)
            self.whereOp[key] = "<"
            #print (self.whereOp[key])
        except Exception:
            self.where[key] = None

    def setWhereValueLTInt(self, key, value):
        try:
            self.where[key] = int(value)
            self.whereOp[key] = "<"
            #print (self.whereOp[key])
        except Exception:
            self.where[key] = None

        #print (self.whereOp[key])
    def setWhereValueGEFloat(self, key, value):
        # Convert to integer
        try:
            self.where[key] = float(value)
            self.whereOp[key] = ">="
        except Exception:
            self.where[key] = None

    def setWhereValueGTFloat(self, key, value):
        # Convert to integer
        try:
            self.where[key] = float(value)
            self.whereOp[key] = ">"
        except Exception:
            self.where[key] = None

    def setWhereAttGTAtt(self, key1, key2):
        # Compare fields
        try:
            self.where[key1] = f"{key2}"
            self.whereOp[key1] = ">"
        except Exception:
            self.where[key1] = None
    def setWhereAttLTAtt(self, key1, key2):
        # Compare fields
        try:
            self.where[key1] = f"{key2}"
            self.whereOp[key1] = "<"
        except Exception:
            self.where[key1] = None

    def setWhereValueFloat(self, key, value):
        # Convert to floating point
        try:
            self.where[key] = float(value)
        except Exception:
            self.where[key] = None

    def setWhereValueInt(self, key, value):
        # Convert to integer
        try:
            self.where[key] = int(value)
        except Exception:
            self.where[key] = None

    def setHavingGTInt(self, key, value):
        try:
            self.having[key] = int(value)
            self.havingOp[key] = ">"
        except Exception:
            self.having = {}
            self.havingOp = {}
            self.having[key] = int(value)
            self.havingOp[key] = ">"
            
    def setGroupByCol(self, key):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        try:
            self.groupBy[key] = None
        except Exception:
            self.groupBy={}
            self.groupBy[key] = None

    def getWhereClause(self):
        loc_WHERE_txt = ""
        for k, v in self.where.items():
            if loc_WHERE_txt:
                loc_WHERE_txt = loc_WHERE_txt + " and "
            else:
                loc_WHERE_txt = " WHERE "
            if v == None:
                v = "Null"
            if isinstance(v, list):
                # List of alternate values
                bracketed = ""
                #print(self.whereOp)
                if k in self.whereOp and self.whereOp[k]=='IN':
                    bracketed= str(k) + " IN " + " ( " + ', '.join([str(x) for x in v])  + " ) "
                elif self.whereOp[k]=='AND':
                    for item in v:
                        if bracketed:
                            bracketed = bracketed + " and " + str(k) + " " + str(item)
                        else:
                            bracketed = str(k) + " " + str(item)
                    bracketed = " ( " + bracketed + " ) "
                else:
                    for item in v:
                        if bracketed:
                            bracketed = bracketed + " or " + str(k) + " " + str(item)
                        else:
                            bracketed = str(k) + " " + str(item)
                    bracketed = " ( " + bracketed + " ) "
                loc_WHERE_txt = loc_WHERE_txt + bracketed
            else:
                try:
                    # Other relationship than equals.
                    loc_WHERE_txt = loc_WHERE_txt + str(k) + " " + self.whereOp[k] + " " + str(v)
                except Exception:
                    # Equals
                    loc_WHERE_txt = loc_WHERE_txt + str(k) + " = " + str(v)
        #print (loc_WHERE_txt)
        return loc_WHERE_txt
        
        
        
    def getGroupByClause(self):
        loc_GROUPBY_txt = ""
        try:
            loc_GROUPBY_txt =  ', '.join([str(x) for x in self.groupBy])  # list comprehension
        except Exception:
            return ''
        
        loc_GROUPBY_txt = " GROUP BY " + loc_GROUPBY_txt 
        #print (loc_GROUPBY_txt)
        return loc_GROUPBY_txt
        
    def getHavingClause(self):
        loc_HAVING_txt = ""
        try:
            for k, v in self.having.items():
                if loc_HAVING_txt:
                    loc_HAVING_txt = loc_HAVING_txt + " and "
                else:
                    loc_HAVING_txt = " HAVING "
                if v == None:
                    v = "Null"
                if isinstance(v, list):
                    # List of alternate values
                    bracketed = ""
                    for item in v:
                        if bracketed:
                            bracketed = bracketed + " or " + str(k) + " " + item
                        else:
                            bracketed = str(k) + " " + item
                    bracketed = " ( " + bracketed + " ) "
                    loc_HAVING_txt = loc_HAVING_txt + bracketed
                else:
                    try:
                        # Other relationship than equals.
                        loc_HAVING_txt = loc_HAVING_txt + str(k) + " " + self.havingOp[k] + " " + str(v)
                    except Exception:
                        # Equals
                        loc_HAVING_txt = loc_HAVING_txt + str(k) + " = " + str(v)
        except Exception:
            return ''
        #print (loc_HAVING_txt)
        return loc_HAVING_txt
        
    def executeIAD(self, SQL):    
        dbCursor=self.connect.cursor()
        print(SQL)
        # Loop round in case of deadlocks
        for i in range(4):
            try:
                dbCursor.execute(SQL)
            except Exception as e:
                if i < 3:
                    time.sleep(1)
                else:
                    print (SQL)
                    frame = inspect.currentframe()
                    # __FILE__
                    fileName  =  frame.f_code.co_filename
                    print ("fileName: "+fileName)
                    # __LINE__
                    fileNo = frame.f_lineno
                    print("fileNo: "+str(fileNo))
                    #print ("%s Line: %d") % (fileName,  fileNo)
                    #print (f'{fileName} Line: {fileNo}')
                    print (e)
            else:
                break
                
        self.connect.commit ()                                                           # Commits changes
        dbCursor.close()
            
class sqlSelect(sql):
    
    def setSortCol(self, key, asc=1):
        # -ve is desc, +ve is ascending
        if asc<0:
            self.sort[key] = "desc"
        else:
            self.sort[key] = "asc"

    def setReturnCol(self, key):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.attribute[key] = None


    def getSQL(self):
        loc_return_fields_txt =  ', '.join([str(x) for x in self.attribute])  # list comprehension
        
        loc_SELECT_txt = "SELECT " + loc_return_fields_txt 
        loc_TABLE_txt = " FROM " + self.table + " "
        
        loc_WHERE_txt = self.getWhereClause()
        loc_GROUPBY_txt = self.getGroupByClause()
        loc_HAVING_txt = self.getHavingClause()

        loc_ORDER_BY_txt = ""
        for k, v in self.sort.items():
            if loc_ORDER_BY_txt:
                loc_ORDER_BY_txt = loc_ORDER_BY_txt + " and "
            else:
                loc_ORDER_BY_txt = " ORDER BY "

            loc_ORDER_BY_txt = loc_ORDER_BY_txt + str(k) + " " + str(v)
            
        loc_SQL_string = loc_SELECT_txt + loc_TABLE_txt + loc_WHERE_txt + loc_GROUPBY_txt + loc_HAVING_txt + loc_ORDER_BY_txt
        
        #print (loc_SQL_string)
        
        return loc_SQL_string

    def selectRecordSet(self):
                    
        loc_SQL_string = self.getSQL()
                
        return self.executeR(loc_SQL_string)
    def executeR(self, SQL):
        
        dbCursor=self.connect.cursor()
        #print(SQL)
        try:
            dbCursor.execute(SQL)
            #self.connect.commit()
        except Exception as e:
            
            frame = inspect.currentframe()
            # __FILE__
            fileName  =  frame.f_code.co_filename
            #print fileName
            # __LINE__
            fileNo = frame.f_lineno
            print (e)
            print (SQL)
            print (f'{fileName} Line: {fileNo}')
        return dbCursor

class sqlInsert(sql):
    
    def setAttributeBool(self, key, value):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.attribute[key] = value
        
    def setAttributeTime(self, key, value):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.attribute[key] = "'"+str(value.strip())+ "'"
    def setAttributeDate(self, key, value):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.attribute[key] = "'"+str(value.strip())+ "'"
    def setAttributeString(self, key, value):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.attribute[key] = "'"+str(value.strip())+ "'"
        #pass
        #self.attribute[key] = "'"+unicode(value.strip(), "utf-8")+"'"
    def setAttributeIntBig(self, key, value):
        # Convert to integer
        try:
            self.attribute[key] = value
        except Exception:
            self.attribute[key] = None
    def setAttributeInteger(self, key, value):
        # Convert to integer
        try:
            self.attribute[key] = int(value)
        except Exception:
            self.attribute[key] = None
    def setAttributeFloat(self, key, value):
        # Convert to floating point
        try:
            self.attribute[key] = float(value)
        except Exception:
            self.attribute[key] = None

    def getInsertSQL(self):
        loc_insert_fields_txt =  ', '.join([str(x) for x in self.attribute])  # list comprehension
        
        loc_insert_values_txt=""
        for k, v in self.attribute.items():
            if loc_insert_values_txt:
                loc_insert_values_txt = loc_insert_values_txt + ", "
            if v == None:
                v = "Null"
                
            if isinstance(v, bool) and v:
                v = "True"
            if isinstance(v, bool) and not v:
                v = "False"
                
            loc_insert_values_txt = loc_insert_values_txt + str(v)
        #
        #   Removes leading and training whitespace from parameters.
        #
        loc_INSERT_INTO_txt = "INSERT INTO " + self.table + " ( " + loc_insert_fields_txt + ") "
        loc_values_txt = "VALUES (" + loc_insert_values_txt + ") ;"
        loc_SQL_string = loc_INSERT_INTO_txt + loc_values_txt
        
        return loc_SQL_string
        
    def insertRecord(self):
        
        loc_SQL_string=self.getInsertSQL()
        #loc_insert_fields_txt =  ', '.join([str(x) for x in self.attribute])  # list comprehension
        #
        #loc_insert_values_txt=""
        #for k, v in self.attribute.items():
        #    if loc_insert_values_txt:
        #        loc_insert_values_txt = loc_insert_values_txt + ", "
        #    if v == None:
        #        v = "Null"
        #    loc_insert_values_txt = loc_insert_values_txt + str(v)
        ##
        ##   Removes leading and training whitespace from parameters.
        ##
        #loc_INSERT_INTO_txt = "INSERT INTO " + self.table + " ( " + loc_insert_fields_txt + ") "
        #loc_values_txt = "VALUES (" + loc_insert_values_txt + ") ;"
        #loc_SQL_string = loc_INSERT_INTO_txt + loc_values_txt
        
        self.executeIAD(loc_SQL_string)
        

class sqlUpdate(sql):
    
    def setAttributeString(self, key, value):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.attribute[key] = "'"+str(value.strip())+ "'"
        
    def setAttributeBool(self, key, value):
        # Trim value to remove whitespace from the start and end of the string
        # convert to string
        self.attribute[key] = value
        
    def setAttributeFloat(self, key, value):
        # Convert to floating point
        try:
            self.attribute[key] = float(value)
        except Exception:
            self.attribute[key] = None
            
    def getUpdateSQL(self):
        loc_SET_txt=""	                                                        # SQL SET clause
        for k, v in self.attribute.items():
            if loc_SET_txt:
                loc_SET_txt = loc_SET_txt + ", "
            else:
                loc_SET_txt = " SET "
            if v == None:
                v = "Null"
            if isinstance(v, bool) and v:
                v = "True"
            if isinstance(v, bool) and not v:
                v = "False"
            loc_SET_txt = loc_SET_txt + k + " = " + str(v)
            

        loc_WHERE_txt = self.getWhereClause()

        #
        #   Removes leading and training whitespace from parameters.
        #
        loc_SQL_string = "UPDATE " + self.table + loc_SET_txt + loc_WHERE_txt +';'
        
        #self.executeIAD(loc_SQL_string)

        return loc_SQL_string

    def updateRecord(self, loc_SQL_string=''):
        #loc_SET_txt=""	                                                        # SQL SET clause
        #for k, v in self.attribute.items():
        #    if loc_SET_txt:
        #        loc_SET_txt = loc_SET_txt + ", "
        #    else:
        #        loc_SET_txt = " SET "
        #    if v == None:
        #        v = "Null"
        #    loc_SET_txt = loc_SET_txt + k + " = " + str(v)
        #    
        #
        #loc_WHERE_txt = self.getWhereClause()
        #
        ##
        ##   Removes leading and training whitespace from parameters.
        ##
        #loc_SQL_string = "UPDATE " + self.table + loc_SET_txt + loc_WHERE_txt 
        if not loc_SQL_string:
            loc_SQL_string=self.getUpdateSQL()
        self.executeIAD(loc_SQL_string)

        return loc_SQL_string

    
class sqlDelete(sql):
    
    def getSQL(self):
        
        loc_DELETE_txt = "DELETE FROM " + self.table + " "
        
        loc_WHERE_txt = self.getWhereClause()

        loc_SQL_string = loc_DELETE_txt + loc_WHERE_txt + "; "
        
        return loc_SQL_string
    def deleteRecordSet(self):

        #loc_DELETE_txt = "DELETE FROM " + self.table + " "
        #
        #loc_WHERE_txt = self.getWhereClause()
        #
        #loc_SQL_string = loc_DELETE_txt + loc_WHERE_txt
        loc_SQL_string=self.getSQL()
        print(loc_SQL_string)
        self.executeIAD(loc_SQL_string)
        
